from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

import logging
import json

logger = logging.getLogger(__name__)


class TestConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)('vis-interaction', self.channel_name)
        async_to_sync(self.channel_layer.group_add)('service-update', self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)('vis-interaction', self.channel_name)
        async_to_sync(self.channel_layer.group_discard)('service-update', self.channel_name)

    def receive(self, text_data=None):
        data = json.loads(text_data)
        type = data['type']

        logger.info(f'Received message with type {type}')

        if type == 'interaction':
            async_to_sync(self.channel_layer.group_send)('vis-interaction', data)
        elif type == 'service.udpate':
            async_to_sync(self.channel_layer.group_send)('service-update', data)

    def interaction(self, event):
        logger.info('Intent: {}'.format(event['intent']))
        self.send(text_data=json.dumps(event))

    def service_update(self, event):
        logger.info(f'Service update: {event["name"]}')
        self.send(text_data=json.dumps(event))
