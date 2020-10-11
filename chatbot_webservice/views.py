from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import viewsets

import json
import logging

from .serializers import ServiceSerializer, DependencySerializer, ServiceDataSerializer, SpecificationSerializer
from .models import Service, Dependency, ServiceData, Specification
from .utils import Utils

logger = logging.getLogger(__name__)


@csrf_exempt
def dialogflow(request):
    logger.info('Dialogflow endpoint received a request')
    req = json.loads(request.body)

    intent = req.get('queryResult').get('intent').get('displayName')

    params = {}

    if intent == 'Select Service':
        params['service_name'] = req.get('queryResult').get('parameters').get('service_name')
    if intent == 'Specification':
        params['service_name'] = req.get('queryResult').get('parameters').get('service_name')
        params['tb_cause'] = req.get('queryResult').get('parameters').get('tb_cause')
        params['initial_loss'] = req.get('queryResult').get('parameters').get('initial_loss')
        params['recovery_time'] = {
            'amount': req.get('queryResult').get('parameters').get('recovery_time').get('amount'),
            'unit': req.get('queryResult').get('parameters').get('recovery_time').get('unit')
        }
        params['loss_of_resilience'] = req.get('queryResult').get('parameters').get('loss_of_resilience')


    # Send message via websockets
    layer = get_channel_layer()
    async_to_sync(layer.group_send)('vis-interaction', {
        'type': 'interaction',
        'intent': intent,
        'params': params
    })

    if intent == 'Show Architecture':
        fulfillmentText = {'fulfillmentText': 'Here is your architecture.'}
    elif intent == 'Show Specification':
        fulfillmentText = {'fulfillmentText': 'Here is you specification.'}
    elif intent == 'Select Service':
        fulfillmentText = {'fulfillmentText': 'I am selecting {}'.format(params.get('service_name'))}
    elif intent == 'Specification':
        fulfillmentText = {'fulfillmentText' : 'I specified the following transient behavior for {} in case of {}: initial loss: {}, recovery time: {}s, loss of resilience: {}'.format(params['service_name'], params['tb_cause'], params['initial_loss'], Utils.duration_to_seconds(params['recovery_time']), params['loss_of_resilience'])}

        service = Service.objects.get(name=params['service_name'])
        Specification.objects.create(
            service=service,
            cause=params['tb_cause'],
            max_initial_loss=params['initial_loss'],
            max_recovery_time=Utils.duration_to_seconds(params['recovery_time']),
            max_lor=params['loss_of_resilience']
        )

    return JsonResponse(fulfillmentText, safe=False)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('id')
    serializer_class = ServiceSerializer


class DependencyViewSet(viewsets.ModelViewSet):
    queryset = Dependency.objects.all()
    serializer_class = DependencySerializer


class ServiceDataViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceDataSerializer

    def get_queryset(self):
        queryset = ServiceData.objects.all().order_by('time')
        service = self.request.query_params.get('service')
        callId = self.request.query_params.get('callid')

        if service:
            queryset = queryset.filter(service_id=service)
        if callId:
            queryset = queryset.filter(callId=callId)

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