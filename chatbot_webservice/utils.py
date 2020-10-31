import numpy as np
from scipy import integrate

from .models import Service, ServiceData, Specification
from .config import Param, TbCause


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

        return duration[Param.AMOUNT] * mult[duration[Param.UNIT]]


class LossService:
    __expected_qos = 100.0
    __qos_threshold = 90.0
    __median_range = 5

    service = None
    cause = None
    max_recovery_time = None

    def __init__(self, service_id, cause, spec_recovery_time):
        self.service = Service.objects.get(id=service_id)
        self.cause = cause
        self.max_recovery_time = spec_recovery_time

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
        while data[current_idx].time < specification_endpoint:
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
                        specification_endpoint = data[start_index].time + self.max_recovery_time

                        if data[end_index].time < specification_endpoint:
                            end_index = self._get_specification_end_index(data, end_index, specification_endpoint)

                        transient_behavior_indices.append([start_index, end_index])
                        transient_behavior_endpoint = data[end_index].time

        return transient_behavior_indices

    def _compute_expected_integral(self, complete_data, start_idx, end_idx):
        data = complete_data[start_idx:end_idx + 1]
        x_list = list(map(lambda item: float(item.time), data))
        y = np.full((end_idx + 1 - start_idx,), self.__expected_qos)
        x = np.array(x_list)

        cum_int = integrate.cumtrapz(y, x, initial=0)
        return cum_int

    def _compute_actual_integral(self, complete_data, start_idx, end_idx):
        data = complete_data[start_idx:end_idx + 1]
        y_list = list(map(lambda item: float(item.qos), data))
        x_list = list(map(lambda item: float(item.time), data))
        y = np.array(y_list)
        x = np.array(x_list)

        cum_int = integrate.cumtrapz(y, x, initial=0)
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
            if self.cause == TbCause.DEPLOYMENT:
                self._add_deplpoyment_loss(item, loss[i])
            if self.cause == TbCause.LOAD_BALANCING:
                self._add_load_balancing_loss(item, loss[i])
        print(f'Added loss to data items')

    def _get_call_ids(self):
        if self.service.name == 'loon-service':
            return [0, 1, 2, 3, 4]
        elif self.service.name == 'loon-service2':
            return [5]
        else:
            return []

    def compute_resilience_loss(self):
        # get all service call_ids
        call_ids = self._get_call_ids()

        for call_id in call_ids:
            # get service data for this call_id
            data = ServiceData.objects.filter(service_id=self.service.id, callId=call_id)

            # find occurrences of transient behavior
            tb_occurrences = self._find_transient_behavior(data)

            # compute resilience loss for each of those occurrences
            for tb in tb_occurrences:
                exp_integral = self._compute_expected_integral(data, tb[0], tb[1])
                act_integral = self._compute_actual_integral(data, tb[0], tb[1])
                resilience_loss = exp_integral - act_integral

                # add the computed loss to the service data for this call_id
                self._add_loss_to_data_objects(data, tb, resilience_loss)

        # inform visualization that new loss data is available
        # TODO
