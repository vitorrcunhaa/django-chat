import logging
from datetime import datetime, timedelta

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.core.cache import cache

from members.models import Members
from .models import Group, Message
import json

logger = logging.getLogger('chat')


class JoinAndLeave(WebsocketConsumer):
    def connect(self):
        self.room_uuid = self.scope['url_route']['kwargs']['uuid']
        self.room_group_name = f'chat_{self.room_uuid}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = self.scope['user'].user_id
        user = Members.objects.get(user_id=user_id)

        if self.is_rate_limited(user_id):
            error_message = 'Rate limit exceeded. Try again later.'
            self.send(text_data=json.dumps({'error': error_message}))
            self.log_message(user, message, rate_limited=True)
            return

        group = Group.objects.get(uuid=self.room_uuid)

        db_insert = Message(author=user, content=message, group=group)
        db_insert.save()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {'type': 'chat_message', 'message': f'{user.username}: {message}'}
        )

        self.log_message(user, message)

    def is_rate_limited(self, user_id):
        now = datetime.now()
        cache_key = f"throttle_{user_id}"

        message_times = cache.get(cache_key, [])

        # Filter out messages older than 1 minute
        message_times = [t for t in message_times if t > now - timedelta(minutes=1)]

        if len(message_times) >= 10:
            return True

        # Add current time and update cache
        message_times.append(now)
        cache.set(cache_key, message_times, timeout=60)
        return False

    def log_message(self, user, message, rate_limited=False):
        log_entry = {
            'user': user.username,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'rate_limited': rate_limited,
        }
        logger.info(json.dumps(log_entry))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({'message': message}))
