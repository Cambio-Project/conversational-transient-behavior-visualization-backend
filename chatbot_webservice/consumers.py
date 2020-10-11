from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

import logging
import json

logger = logging.getLogger(__name__)


class TestConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)('vis-interaction', self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)('vis-interaction', self.channel_name)

    def receive(self, text_data=None):
        data = json.loads(text_data)
        intent = data['intent']
        params = data['params']
        async_to_sync(self.channel_layer.group_send)('vis-interaction', {
            'type': 'interaction',
            'intent': intent,
            'params': params
        })

    def interaction(self, event):
        intent = event['intent']
        params = event['params']

        logger.info('Intent: {}'.format(intent))
        self.send(text_data=json.dumps({
            'intent': intent,
            'params': params
        }))
