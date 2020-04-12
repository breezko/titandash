from channels.generic.websocket import WebsocketConsumer

from asgiref.sync import async_to_sync

import json


class QueuedFunctionConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = "queued"
        self.room_group_name = "titan_{name}".format(name=self.room_name)

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        self.send(text_data=json.dumps({
            "data": text_data_json
        }))

    def saved(self, event):
        self.send(text_data=json.dumps({
            "type": "saved",
            "queued": event
        }))

    def finished(self, event):
        self.send(text_data=json.dumps({
            "type": "finished",
            "queued": event
        }))


class LogRecordConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = "log"
        self.room_group_name = "titan_{name}".format(name=self.room_name)

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        self.send(text_data=json.dumps({
            "data": text_data_json
        }))

    def emitted(self, event):
        self.send(text_data=json.dumps({
            "type": "emitted",
            "record": event
        }))


class BotInstanceConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = "instance"
        self.room_group_name = "titan_{name}".format(name=self.room_name)

    def connect(self):
        """Connect to the instance room group."""
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        """Disconnect from the room group."""
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        self.send(text_data=json.dumps({
            "data": text_data_json
        }))

    def saved(self, event):
        self.send(text_data=json.dumps({
            "type": "instance.saved",
            "instance": event
        }))


class PrestigeConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = "prestige"
        self.room_group_name = "titan_{name}".format(name=self.room_name)

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        self.send(text_data=json.dumps({
            "data": text_data_json
        }))

    def saved(self, event):
        self.send(text_data=json.dumps({
            "type": "prestige.saved",
            "prestige": event
        }))
