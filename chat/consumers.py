from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import ChatRoom, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room = await self.get_room(self.scope['url_route']['kwargs']['slug'])
        if self.room is None:
            await self.close(code=4404)
            return
        self.group_name = f'chatroom_{self.room.slug}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        username = str(content.get('username', '')).strip()
        if not await self.validate_username(username):
            await self.send_json({'type': 'error', 'message': 'Please enter a valid username.'})
            return
        text = str(content.get('message', '')).strip()
        if not text:
            await self.send_json({'type': 'error', 'message': 'Message cannot be empty.'})
            return
        if len(text) > 2000:
            await self.send_json({'type': 'error', 'message': 'Message must be 2000 characters or fewer.'})
            return
        message = await self.save_message(username, text)
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'message': message.content,
            'username': message.username,
            'timestamp': message.timestamp.isoformat(),
        })

    async def chat_message(self, event):
        await self.send_json({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        })

    @database_sync_to_async
    def get_room(self, slug):
        try:
            return ChatRoom.objects.get(slug=slug)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, username, content):
        return Message.objects.create(room=self.room, username=username, content=content)

    @database_sync_to_async
    def validate_username(self, username):
        return 1 <= len(username) <= 50 and all(
            character.isalnum() or character in ' _-' for character in username
        )
