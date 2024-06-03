from django.contrib.auth import get_user_model
from django.test import TestCase
from chat.models import Group, Message
import uuid

User = get_user_model()


class ChatModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@user.com', password='testpassword')
        self.group = Group.objects.create(uuid=uuid.uuid4())

    def test_group_creation(self):
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(str(self.group.uuid), str(self.group.uuid))

    def test_add_remove_user(self):
        self.group.add_user(self, self.user)
        self.assertIn(self.user, self.group.members.all())
        self.group.remove_user(self, self.user)
        self.assertNotIn(self.user, self.group.members.all())

    def test_message_creation(self):
        message = Message.objects.create(author=self.user, content="Hello, world!", group=self.group)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.content, "Hello, world!")
