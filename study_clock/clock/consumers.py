import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from clock.models import PrivateMessage
from clock.serializers import PrivateMessageSerializer

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.chat_user_id = self.scope['url_route']['kwargs']['user_id']
        self.chat_room = f'chat_{self.user.id}_{self.chat_user_id}'

        if self.user.is_authenticated:
            await self.channel_name.group_add(self.chat_room, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.chat_room, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('content')

        if self.user.is_authenticated and content:
            message = PrivateMessage.objects.create(
                sender=self.user,
                receiver_id=self.chat_user_id,
                content=content,
            )

            serializer = PrivateMessageSerializer(message)

            await self.channel_layer.group_send(
                self.chat_room,
                {
                    'type': 'chat_message',
                    'message': serializer.data
                }
            )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = 'support_chat'
#
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         username = self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonymous'
#
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username': username
#             }
#         )
#
#     async def chat_message(self, event):
#         message = event['message']
#         username = event['username']
#
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'username': username
#         }))
