import numpy as np
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Service, ServiceData, Specification
from .config import Param, TbCause
from .math import Math


class Utils:

    @staticmethod
    def duration_to_seconds(duration):
        mult = {
            's': 1,
            'min': 60,
            'h': 60 * 60,
            'day': 60 * 60 * 24,
            'wk': 60 * 60 * 24 * 7,
            'mo': -1,
            'yr': -1,
            'decade': -1
        }

        return float(duration[Param.AMOUNT] * mult[duration[Param.UNIT]])


class LossService:
    __expected_qos = 100.0
    __qos_threshold = 90.0
    __median_range = 5

    service = None
    cause = None
    max_recovery_time = None
    max_loss = None

    def __init__(self, service, cause, spec_recovery_time, max_loss):
        self.service = service
        self.cause = cause
        self.max_recovery_time = spec_recovery_time
        self.max_loss = max_loss

    def _get_next_items(self, data, idx):
        last_index = idx + self.__median_range if idx + self.__median_range < len(data) else len(data) - 1
        return data[idx:last_index]

    def _median_of_items(self, data, idx):
        next_items = self._get_next_items(data, idx)
        next_qos = list(map(lambda item: item.qos, next_items))
        return np.median(next_qos)

    def _is_initial_loss(self, data, idx):
        median = self._median_of_items(data, idx)
        if median < self.__qos_threshold:
            return True
        return False

    def _get_start_index(self, data, idx):
        next_items = self._get_next_items(data, idx)
        minimum = data[idx]
        min_idx = idx

        for j, item in enumerate(next_items):
            if item.qos < minimum.qos:
                minimum = item
                min_idx = idx + j

        return min_idx

    def _get_end_index(self, data, idx):
        remaining_data = data[idx + 1:len(data)]

        for j, item in enumerate(remaining_data):
            if item.qos >= self.__expected_qos:
                median = self._median_of_items(remaining_data, j)
                if median >= self.__qos_threshold:
                    return idx + 1 + j
        return len(data) - 1

    def _get_specification_end_index(self, data, idx, specification_endpoint):
        current_idx = idx
        while current_idx < len(data) - 1 and data[current_idx].time < specification_endpoint:
            current_idx += 1
        return current_idx

    def _find_transient_behavior(self, data):
        specification_endpoint = -1.0
        transient_behavior_endpoint = -1.0

        transient_behavior_indices = []

        for i, item in enumerate(data):
            if item.time > specification_endpoint and item.time > transient_behavior_endpoint:
                if item.qos < self.__expected_qos:
                    if self._is_initial_loss(data, i):
                        start_index = self._get_start_index(data, i)
                        end_index = self._get_end_index(data, start_index)
                        specification_endpoint = float(data[start_index].time) + self.max_recovery_time

                        if data[end_index].time < specification_endpoint:
                            end_index = self._get_specification_end_index(data, end_index, specification_endpoint)

                        transient_behavior_indices.append([start_index, end_index])
                        transient_behavior_endpoint = data[end_index].time

        return transient_behavior_indices

    def _compute_expected_integral(self, complete_data, start_idx, end_idx):
        data = complete_data[start_idx:end_idx + 1]
        x = list(map(lambda item: float(item.time), data))
        y = [self.__expected_qos] * len(x)

        cum_int = Math.integrate(y, x)
        return cum_int

    def _compute_actual_integral(self, complete_data, start_idx, end_idx):
        data = complete_data[start_idx:end_idx + 1]
        y = list(map(lambda item: float(item.qos), data))
        x = list(map(lambda item: float(item.time), data))

        cum_int = Math.integrate(y, x)
        return cum_int

    def _add_failure_loss(self, item, loss):
        item.failureLoss = loss
        item.save()

    def _add_deployment_loss(self, item, loss):
        item.deploymentLoss = loss
        item.save()

    def _add_load_balancing_loss(self, item, loss):
        item.loadBalancingLoss = loss
        item.save()

    def _add_loss_to_data_objects(self, data, tb, loss):
        tb_start_idx = tb[0]
        tb_end_idx = tb[1]
        relevant_data = data[tb_start_idx:tb_end_idx + 1]

        for i, item in enumerate(relevant_data):
            if self.cause == TbCause.FAILURE:
                self._add_failure_loss(item, loss[i])
            elif self.cause == TbCause.DEPLOYMENT:
                self._add_deployment_loss(item, loss[i])
            elif self.cause == TbCause.LOAD_BALANCING:
                self._add_load_balancing_loss(item, loss[i])
        print(f'Added loss to data items')

    def _get_call_ids(self):
        if self.service.name == 'loon-service2':
            return [5]
        else:
            num_endpoints = len(self.service.endpoints)
            call_ids = []
            for i in range(0, num_endpoints):
                call_ids.append(i)
            return call_ids

    def _reset_loss(self):
        data = ServiceData.objects.filter(service_id=self.service.id)
        if self.cause == TbCause.FAILURE:
            data.update(failureLoss=0.0)
        elif self.cause == TbCause.DEPLOYMENT:
            data.update(deploymentLoss=0.0)
        elif self.cause == TbCause.LOAD_BALANCING:
            data.update(loadBalancingLoss=0.0)

    def _get_violations(self):
        if self.cause == TbCause.FAILURE:
            return ServiceData.objects.filter(service_id=self.service.id, failureLoss__gt=self.max_loss)
        elif self.cause == TbCause.DEPLOYMENT:
            return ServiceData.objects.filter(service_id=self.service.id, deploymentLoss__gt=self.max_loss)
        elif self.cause == TbCause.LOAD_BALANCING:
            return ServiceData.objects.filter(service_id=self.service.id, loadBalancingLoss__gt=self.max_loss)

    def _reevaluate_loss_violations(self):
        violations = []

        if self.cause == TbCause.FAILURE:
            try:
                max_deployment_loss = Specification.objects.get(service_id=self.service.id, cause=TbCause.DEPLOYMENT).max_lor
                violations += ServiceData.objects.filter(service_id=self.service.id,
                                                         deploymentLoss__gt=max_deployment_loss)
            except Specification.DoesNotExist:
                pass
            try:
                max_load_balancing_loss = Specification.objects.get(service_id=self.service.id, cause=TbCause.LOAD_BALANCING).max_lor
                violations += ServiceData.objects.filter(service_id=self.service.id,
                                                         loadBalancingLoss__gt=max_load_balancing_loss)
            except Specification.DoesNotExist:
                pass
        elif self.cause == TbCause.DEPLOYMENT:
            try:
                max_failure_loss = Specification.objects.get(service_id=self.service.id, cause=TbCause.FAILURE).max_lor
                violations += ServiceData.objects.filter(service_id=self.service.id, deploymentLoss__gt=max_failure_loss)
            except Specification.DoesNotExist:
                pass
            try:
                max_load_balancing_loss = Specification.objects.get(service_id=self.service.id, cause=TbCause.LOAD_BALANCING).max_lor
                violations += ServiceData.objects.filter(service_id=self.service.id, loadBalancingLoss__gt=max_load_balancing_loss)
            except Specification.DoesNotExist:
                pass
        elif self.cause == TbCause.LOAD_BALANCING:
            try:
                max_failure_loss = Specification.objects.get(service_id=self.service.id, cause=TbCause.FAILURE).max_lor
                violations += ServiceData.objects.filter(service_id=self.service.id, deploymentLoss__gt=max_failure_loss)
            except Specification.DoesNotExist:
                pass
            try:
                max_deployment_loss = Specification.objects.get(service_id=self.service.id, cause=TbCause.DEPLOYMENT).max_lor
                violations += ServiceData.objects.filter(service_id=self.service.id, deploymentLoss__gt=max_deployment_loss)
            except Specification.DoesNotExist:
                pass

        if violations:
            self._update_service_object(True)
        else:
            self._update_service_object(False)

    def _notify_viz(self):
        layer = get_channel_layer()
        async_to_sync(layer.group_send)('service-update', {
            'type': 'service.update',
            'id': self.service.id,
            'name': self.service.name,
            'system': self.service.system,
            'endpoints': self.service.endpoints,
            'violation_detected': self.service.violation_detected
        })

    def _update_service_object(self, has_violations):
        if self.service.violation_detected != has_violations:
            self.service.violation_detected = has_violations
            self.service.save()
            self._notify_viz()

    def compute_resilience_loss(self):
        self._reset_loss()

        call_ids = self._get_call_ids()
        for call_id in call_ids:
            data = ServiceData.objects.filter(service_id=self.service.id, callId=call_id).order_by('time')
            tb_occurrences = self._find_transient_behavior(data)

            for tb in tb_occurrences:
                exp_integral = self._compute_expected_integral(data, tb[0], tb[1])
                act_integral = self._compute_actual_integral(data, tb[0], tb[1])

                resilience_loss = []
                for i in range(len(exp_integral)):
                    loss = exp_integral[i] - act_integral[i]
                    resilience_loss.append(loss)

                self._add_loss_to_data_objects(data, tb, resilience_loss)

    def remove_resilience_loss(self):
        self._reset_loss()
        self._reevaluate_loss_violations()

    def check_loss_violations(self):
        violations = self._get_violations()

        if violations:
            self._update_service_object(True)
        else:
            self._update_service_object(False)
