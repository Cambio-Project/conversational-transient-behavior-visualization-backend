from django.shortcuts import render
from django.http import HttpResponse

import logging

logger = logging.getLogger(__name__)


def dialogflow(request):
    logger.info('Dialogflow endpoint received a request')
    return HttpResponse("Hello World. You are looking at the dialogflow endpoint.")