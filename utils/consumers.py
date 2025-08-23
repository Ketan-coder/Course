# yourapp/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MetricsConsumer(AsyncWebsocketConsumer):
    group = "metrics"

    async def connect(self):
        if self.scope["user"].is_staff:  # gate admin only
            await self.channel_layer.group_add(self.group, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def metrics_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

class SecurityConsumer(AsyncWebsocketConsumer):
    group = "security"

    async def connect(self):
        if self.scope["user"].is_staff:
            await self.channel_layer.group_add(self.group, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def security_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

class RecordsConsumer(AsyncWebsocketConsumer):
    group = "records"

    async def connect(self):
        if self.scope["user"].is_staff:
            await self.channel_layer.group_add(self.group, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def records_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))