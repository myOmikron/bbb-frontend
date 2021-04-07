from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from chat.models import Chat


channel_layer = get_channel_layer()


@receiver(post_save, sender=Chat, dispatch_uid="on_chat_save")
def on_chat_save(chat: Chat, **kwargs):
    async_to_sync(channel_layer.group_send)(chat.channel.meeting_id, {
        "type": "update.db",
        "chat": dict((key, value) for key, value in chat.__dict__ if not key.startswith("_"))
    })


@receiver(pre_delete, sender=Chat, dispatch_uid="on_chat_delete")
def on_chat_delete(chat: Chat, **kwargs):
    async_to_sync(channel_layer.group_send)(chat.channel.meeting_id, {
        "type": "update.db",
        "chat": None
    })
