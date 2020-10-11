from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import viewsets

import json
import logging

from .serializers import ServiceSerializer, DependencySerializer, ServiceDataSerializer
from .models import Service, Dependency, ServiceData

logger = logging.getLogger(__name__)


@csrf_exempt
def dialogflow(request):
    logger.info('Dialogflow endpoint received a request')
    req = json.loads(request.body)

    intent = req.get('queryResult').get('intent').get('displayName')
    param = req.get('queryResult').get('parameters').get('service_name')

    # Send message via websockets
    layer = get_channel_layer()
    async_to_sync(layer.group_send)('vis-interaction', {
        'type': 'interaction',
        'intent': intent,
        'param': param
    })

    if intent == 'Show Architecture':
        fulfillmentText = {'fulfillmentText': 'Here is your architecture.'}
    elif intent == 'Show Specification':
        fulfillmentText = {'fulfillmentText': 'Here is you specification.'}
    elif intent == 'Select Service':
        fulfillmentText = {'fulfillmentText': 'I am selecting {}'.format(param)}

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
