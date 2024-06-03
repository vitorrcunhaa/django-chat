from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from chat.models import Group
import uuid

User = get_user_model()


class ChatViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@user.com', password='testpassword')
        self.group = Group.objects.create(uuid=uuid.uuid4())
        self.group.members.add(self.user)
        self.group.save()

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_new_group(self):
        self.client.login(username='test@user.com', password='testpassword')
        response = self.client.post(reverse('new_group'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(Group.objects.count(), 2)

    def test_join_group(self):
        new_user = User.objects.create_user(email='new@user.com', password='newpassword')
        self.client.login(email='new@user.com', password='newpassword')
        response = self.client.post(reverse('join_group', args=[str(self.group.uuid)]))
        self.assertRedirects(response, reverse('home'))
        self.assertIn(new_user, self.group.members.all())

    def test_leave_group(self):
        self.client.login(email='test@user.com', password='testpassword')
        response = self.client.post(reverse('leave_group', args=[str(self.group.uuid)]))
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn(self.user, self.group.members.all())

    def test_open_chat(self):
        self.client.login(email='test@user.com', password='testpassword')
        response = self.client.get(reverse('open_chat', args=[str(self.group.uuid)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat.html')

    def test_remove_group(self):
        self.client.login(email='test@user.com', password='testpassword')
        response = self.client.post(reverse('remove_group', args=[str(self.group.uuid)]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(Group.objects.count(), 0)
