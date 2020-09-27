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

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        logger.info('Received data: {}'.format(text_data_json))