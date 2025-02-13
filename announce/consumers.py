import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ELW.models import Teachers, Students

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['session'].get('username')
        self.role = self.scope['session'].get('role', 'none')
        if self.username:
            self.room_group_name = f'user_{self.username}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        if action == 'send_notification':
            message = text_data_json['message']
            post_id = text_data_json.get('post_id')
            announcement_id = text_data_json.get('announcement_id')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'notification_message',
                    'message': message,
                    'post_id': post_id,
                    'announcement_id': announcement_id,
                }
            )

    async def notification_message(self, event):
        message = event['message']
        post_id = event.get('post_id')
        announcement_id = event.get('announcement_id')
        await self.send(text_data=json.dumps({
            'message': message,
            'post_id': post_id,
            'announcement_id': announcement_id,
        }))