from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json
import logging

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