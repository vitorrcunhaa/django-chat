from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns
from chat.models import Group
import uuid
import json
import asyncio
from asgiref.sync import sync_to_async

User = get_user_model()


class ChatConsumerTestCase(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test2@user.com', password='testpassword2')
        self.group = Group.objects.create(uuid=uuid.uuid4())
        self.group.members.add(self.user)
        self.group.save()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Define the application
        self.application = ProtocolTypeRouter({
            "websocket": AuthMiddlewareStack(
                URLRouter(
                    websocket_urlpatterns
                )
            ),
        })

    async def connect_and_authenticate(self, communicator):
        await communicator.connect()
        communicator.scope["user"] = self.user
        communicator.scope["session"].save()
        communicator.scope["user"].backend = 'django.contrib.auth.backends.ModelBackend'
        return communicator

    async def test_connect(self):
        communicator = WebsocketCommunicator(self.application, f"/ws/open_chat/{self.group.uuid}/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_receive_message(self):
        communicator = WebsocketCommunicator(self.application, f"/ws/open_chat/{self.group.uuid}/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        communicator.scope['user'] = self.user
        communicator.scope["session"].save()
        communicator.scope["user"].backend = 'django.contrib.auth.backends.ModelBackend'

        message_data = json.dumps({"message": "Hello, world!"})
        await communicator.send_to(text_data=message_data)

        response = await communicator.receive_from()
        response_data = json.loads(response)

        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'test2@user.com: Hello, world!')

        await communicator.disconnect()

    async def test_rate_limiting(self):
        communicator = WebsocketCommunicator(self.application, f"/ws/open_chat/{self.group.uuid}/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        communicator.scope['user'] = self.user
        communicator.scope["session"].save()
        communicator.scope["user"].backend = 'django.contrib.auth.backends.ModelBackend'

        message_data = json.dumps({"message": "Hello, world!"})

        # Send 10 messages to hit rate limit
        for _ in range(10):
            await communicator.send_to(text_data=message_data)
            response = await communicator.receive_from()
            response_data = json.loads(response)
            self.assertIn('message', response_data)
            self.assertEqual(response_data['message'], 'test2@user.com: Hello, world!')

        # The 11th message should trigger rate limiting
        await communicator.send_to(text_data=message_data)
        response = await communicator.receive_from()
        response_data = json.loads(response)

        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Rate limit exceeded. Try again later.')

        await communicator.disconnect()

    async def test_logging(self):
        communicator = WebsocketCommunicator(self.application, f"/ws/open_chat/{self.group.uuid}/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        communicator.scope['user'] = self.user
        communicator.scope["session"].save()
        communicator.scope["user"].backend = 'django.contrib.auth.backends.ModelBackend'

        message_data = json.dumps({"message": "Test logging message"})
        await communicator.send_to(text_data=message_data)

        response = await communicator.receive_from()
        response_data = json.loads(response)

        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'test2@user.com: Test logging message')

        await communicator.disconnect()

    async def test_join_and_leave_group(self):
        new_user = await sync_to_async(User.objects.create_user)(email='new@user.com', password='newpassword')
        await sync_to_async(self.client.login)(email='new@user.com', password='newpassword')

        response = await sync_to_async(self.client.post)(f'/join_group/{self.group.uuid}/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(await sync_to_async(self.group.members.filter(id=new_user.id).exists)())

        response = await sync_to_async(self.client.post)(f'/leave_group/{self.group.uuid}/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(await sync_to_async(self.group.members.filter(id=new_user.id).exists)())


# Asynchronous test runner for Django
def async_test(f):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(*args, **kwargs))

    return wrapper


class AsyncChatConsumerTestCase(ChatConsumerTestCase):
    @async_test
    async def test_connect(self):
        await super().test_connect()

    @async_test
    async def test_receive_message(self):
        await super().test_receive_message()

    @async_test
    async def test_rate_limiting(self):
        await super().test_rate_limiting()

    @async_test
    async def test_logging(self):
        await super().test_logging()

    @async_test
    async def test_join_and_leave_group(self):
        await super().test_join_and_leave_group()
