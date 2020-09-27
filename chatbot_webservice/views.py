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
    fulfillmentText = {'fulfillmentText': 'This is a test response sent from the webhook.'}
    return JsonResponse(fulfillmentText, safe=False)
