from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TestCase, override_settings

from config.asgi import application
from .models import ChatRoom, Message


@override_settings(
    CHANNEL_LAYERS={
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    },
)
class ChatTests(TestCase):
    def setUp(self):
        self.room = ChatRoom.objects.create(name='General')
        self.other_room = ChatRoom.objects.create(name='Random')

    def test_home_accepts_username_and_creates_room(self):
        response = self.client.post('/', {'username': 'Alice', 'name': 'New room'})
        self.assertRedirects(response, '/rooms/new-room/')
        self.assertEqual(self.client.session['username'], 'Alice')
        self.assertTrue(ChatRoom.objects.filter(name='New room').exists())

    def test_invalid_username_is_rejected(self):
        response = self.client.post('/', {'username': 'bad<script>', 'name': 'Room'})
        self.assertContains(response, 'Username must be')
        self.assertEqual(ChatRoom.objects.count(), 2)

    async def test_messages_are_scoped_to_the_room_and_persisted(self):
        first = WebsocketCommunicator(application, f'/ws/chat/{self.room.slug}/')
        second = WebsocketCommunicator(application, f'/ws/chat/{self.room.slug}/')
        unrelated = WebsocketCommunicator(application, f'/ws/chat/{self.other_room.slug}/')
        connected = [await communicator.connect() for communicator in (first, second, unrelated)]
        self.assertEqual(connected, [(True, None), (True, None), (True, None)])

        await first.send_json_to({'username': 'Alice', 'message': 'Hello everyone'})
        self.assertEqual((await second.receive_json_from())['message'], 'Hello everyone')
        self.assertEqual((await first.receive_json_from())['username'], 'Alice')
        self.assertEqual(await unrelated.receive_nothing(), True)
        saved = await database_sync_to_async(lambda: Message.objects.get())()
        self.assertEqual(saved.room_id, self.room.id)
        self.assertEqual(saved.username, 'Alice')

        await first.disconnect()
        await second.disconnect()
        await unrelated.disconnect()
