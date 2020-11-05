from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import viewsets

import json
import logging

from .serializers import ServiceSerializer, DependencySerializer, ServiceDataSerializer, SpecificationSerializer
from .models import Service, Dependency, ServiceData, Specification
from .utils import Utils, LossService
from .config import Intent, Param, ReqParam

logger = logging.getLogger(__name__)


@csrf_exempt
def dialogflow(request):
    logger.info('Dialogflow endpoint received a request')
    req = json.loads(request.body)
    query_result = req.get(ReqParam.QUERY_RESULT)
    intent = query_result.get(ReqParam.INTENT).get(ReqParam.DISPLAY_NAME)
    query_params = query_result.get(ReqParam.PARAMETERS)

    logger.info(f'INTENT: {intent}')
    params = {}

    if intent == Intent.SELECT_SERVICE:
        params[Param.SERVICE_NAME] = query_params.get(ReqParam.SERVICE_NAME)
        fulfillmentText = {'fulfillmentText': 'I am selecting {}'.format(params.get('service_name'))}
    elif intent == Intent.ADD_SPECIFICATION:
        params[Param.SERVICE_NAME] = query_params.get(ReqParam.SERVICE_NAME)
        params[Param.SCENARIO] = query_params.get(ReqParam.SCENARIO)
        params[Param.TB_CAUSE] = query_params.get(ReqParam.TB_CAUSE)
        params[Param.INITIAL_LOSS] = query_params.get(ReqParam.INITIAL_LOSS)
        params[Param.RECOVERY_TIME] = {
            Param.AMOUNT: query_params.get(ReqParam.RECOVERY_TIME).get(ReqParam.AMOUNT),
            Param.UNIT: query_params.get(ReqParam.RECOVERY_TIME).get(ReqParam.UNIT)
        }
        params[Param.LOSS_OFF_RESILIENCE] = query_params.get(ReqParam.LOSS_OFF_RESILIENCE)

        if params[Param.LOSS_OFF_RESILIENCE] == '':
            max_recovery_duration = Utils.duration_to_seconds(params[Param.RECOVERY_TIME])
            params[Param.LOSS_OFF_RESILIENCE] = (params[Param.INITIAL_LOSS] * max_recovery_duration) / 2

        # Create specification object
        service = Service.objects.get(name=params[Param.SERVICE_NAME], scenario=params[Param.SCENARIO])
        Specification.objects.create(
            service=service,
            cause=params[Param.TB_CAUSE],
            max_initial_loss=params[Param.INITIAL_LOSS],
            max_recovery_time=Utils.duration_to_seconds(params[Param.RECOVERY_TIME]),
            max_lor=params[Param.LOSS_OFF_RESILIENCE]
        )

        # Compute resilience loss
        ls = LossService(service, params[Param.TB_CAUSE], Utils.duration_to_seconds(params[Param.RECOVERY_TIME]), params[Param.LOSS_OFF_RESILIENCE])
        ls.compute_resilience_loss()
        ls.check_loss_violations()


        fulfillmentText = {
            'fulfillmentText': 'I specified the following transient behavior for {} in case of {}: initial loss: {}, recovery time: {}s, loss of resilience: {}'.format(
                params[Param.SERVICE_NAME], params[Param.TB_CAUSE], params[Param.INITIAL_LOSS],
                Utils.duration_to_seconds(params[Param.RECOVERY_TIME]), params[Param.LOSS_OFF_RESILIENCE])}
    elif intent == Intent.DELETE_SPECIFICATION:
        params[Param.SERVICE_NAME] = query_params.get(ReqParam.SERVICE_NAME)
        params[Param.SCENARIO] = query_params.get(ReqParam.SCENARIO)
        params[Param.TB_CAUSE] = query_params.get(ReqParam.TB_CAUSE)

        service = Service.objects.get(name=params[Param.SERVICE_NAME], scenario=params[Param.SCENARIO])

        # Delete specification object
        specification = Specification.objects.get(service=service, cause=params[Param.TB_CAUSE])
        if specification:
            ls = LossService(service, specification.cause, specification.max_recovery_time, specification.max_lor)
            ls.remove_resilience_loss()

            specification.delete()
            fulfillmentText = {'fulfillmentText': f'I deleted the transient behavior specification for {params[Param.TB_CAUSE]} of {params[Param.SERVICE_NAME]}'}
        else:
            fulfillmentText = {'fulfillmentText': f'There is no transient behavior specification for {params[Param.TB_CAUSE]} of {params[Param.SERVICE_NAME]}'}
    elif intent == Intent.EDIT_SPECIFICATION_LOSS:
        logger.info('Entering edit specification loss intent')
        params[Param.SERVICE_NAME] = query_params.get(ReqParam.SERVICE_NAME)
        params[Param.SCENARIO] = query_params.get(ReqParam.SCENARIO)
        params[Param.TB_CAUSE] = query_params.get(ReqParam.TB_CAUSE)
        params[Param.INITIAL_LOSS] = query_params.get(ReqParam.INITIAL_LOSS)

        service = Service.objects.get(name=params[Param.SERVICE_NAME], scenario=params[Param.SCENARIO])

        # Update specification object
        specification = Specification.objects.get(service=service, cause=params[Param.TB_CAUSE])
        if specification:
            new_loss = (params[Param.INITIAL_LOSS] * specification.max_recovery_time) / 2
            specification.max_initial_loss = params[Param.INITIAL_LOSS]
            specification.max_lor = new_loss
            specification.save()

            # Compute resilience loss
            ls = LossService(service, params[Param.TB_CAUSE], specification.max_recovery_time,
                             new_loss)
            ls.compute_resilience_loss()
            ls.check_loss_violations()

            fulfillmentText = {'fulfillmentText': f'Updated the initial loss for {params[Param.TB_CAUSE]} of {params[Param.SERVICE_NAME]} to {params[Param.INITIAL_LOSS]}'}
        else:
            logger.info('Did not find specification object')
            fulfillmentText = {'fulfillmentText': f'There is no transient behavior specification for {params[Param.TB_CAUSE]} of {params[Param.SERVICE_NAME]}'}
    elif intent == Intent.EDIT_SPECIFICATION_RECOVERY_TIME:
        params[Param.SERVICE_NAME] = query_params.get(ReqParam.SERVICE_NAME)
        params[Param.SCENARIO] = query_params.get(ReqParam.SCENARIO)
        params[Param.TB_CAUSE] = query_params.get(ReqParam.TB_CAUSE)
        params[Param.RECOVERY_TIME] = {
            Param.AMOUNT: query_params.get(ReqParam.RECOVERY_TIME).get(ReqParam.AMOUNT),
            Param.UNIT: query_params.get(ReqParam.RECOVERY_TIME).get(ReqParam.UNIT)
        }

        service = Service.objects.get(name=params[Param.SERVICE_NAME], scenario=params[Param.SCENARIO])

        # Update specification object
        specification = Specification.objects.get(service=service,
                                                  cause=params[Param.TB_CAUSE])
        if specification:
            new_recovery_time = Utils.duration_to_seconds(params[Param.RECOVERY_TIME])
            new_loss = (specification.max_initial_loss * new_recovery_time) / 2
            specification.max_recovery_time = Utils.duration_to_seconds(params[Param.RECOVERY_TIME])
            specification.max_lor = new_loss
            specification.save()

            # Compute resilience loss
            ls = LossService(service, params[Param.TB_CAUSE], new_recovery_time,
                             new_loss)
            ls.compute_resilience_loss()
            ls.check_loss_violations()

            fulfillmentText = {
                'fulfillmentText': f'Updated the recovery time for {params[Param.TB_CAUSE]} of {params[Param.SERVICE_NAME]} to {Utils.duration_to_seconds(params[Param.RECOVERY_TIME])} s'}
        else:
            fulfillmentText = {
                'fulfillmentText': f'There is no transient behavior specification for {params[Param.TB_CAUSE]} of {params[Param.SERVICE_NAME]}'}
    elif intent == Intent.SHOW_SPECIFICATION:
        fulfillmentText = {'fulfillmentText': 'Here is you specification.'}
        params[Param.TB_CAUSE] = query_params.get(ReqParam.TB_CAUSE)

    # Send message via websockets
    layer = get_channel_layer()
    async_to_sync(layer.group_send)('vis-interaction', {
        'type': 'interaction',
        'intent': intent,
        'params': params
    })

    return JsonResponse(fulfillmentText, safe=False)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        queryset = Service.objects.all().order_by('id')
        system = self.request.query_params.get('system')
        scenario = self.request.query_params.get('scenario')

        if system:
            queryset = queryset.filter(system=system).order_by('id')
        if scenario:
            queryset = queryset.filter(scenario=scenario).order_by('id')

        return queryset


class DependencyViewSet(viewsets.ModelViewSet):
    serializer_class = DependencySerializer

    def get_queryset(self):
        queryset = Dependency.objects.all()
        system = self.request.query_params.get('system')
        scenario = self.request.query_params.get('scenario')

        if system:
            queryset = queryset.filter(system=system)
        if scenario:
            queryset = queryset.filter(scenario=scenario)

        return queryset


class ServiceDataViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceDataSerializer

    def get_queryset(self):
        queryset = ServiceData.objects.all().order_by('time')
        service = self.request.query_params.get('service')
        callId = self.request.query_params.get('callid')

        if service:
            queryset = queryset.filter(service_id=service).order_by('time')
        if callId:
            queryset = queryset.filter(callId=callId).order_by('time')

        return queryset


class SpecificationViewSet(viewsets.ModelViewSet):
    serializer_class = SpecificationSerializer

    def get_queryset(self):
        queryset = Specification.objects.all().order_by('service')
        service = self.request.query_params.get('service')
        cause = self.request.query_params.get('cause')

        if service:
            queryset = queryset.filter(service_id=service)
        if cause:
            queryset = queryset.filter(cause=cause)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            service = data['service']
            cause = data['cause']
            max_recovery_time = data['max_recovery_time']
            max_loss = data['max_lor']

            ls = LossService(service, cause, max_recovery_time, max_loss)
            ls.compute_resilience_loss()
            ls.check_loss_violations()

        return super().create(request, args, kwargs)

    def destroy(self, request, *args, **kwargs):
        spec = self.get_object()
        service = spec.service
        cause = spec.cause
        max_recovery_time = spec.max_recovery_time
        max_loss = spec.max_lor

        ls = LossService(service, cause, max_recovery_time, max_loss)
        ls.remove_resilience_loss()

        return super().destroy(request, args, kwargs)
