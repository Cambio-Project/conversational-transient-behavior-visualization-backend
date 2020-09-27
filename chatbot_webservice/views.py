from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def dialogflow(request):
    logger.info('Dialogflow endpoint received a request')
    req = json.loads(request.body)
    intent = req.get('queryResult').get('intent').get('displayName')

    if intent == 'Show Architecture':
        fulfillmentText = {'fulfillmentText': 'Here is your architecture.'}
    elif intent == 'Show Specification':
        fulfillmentText = {'fulfillmentText': 'Here is you specification.'}

    return JsonResponse(fulfillmentText, safe=False)
