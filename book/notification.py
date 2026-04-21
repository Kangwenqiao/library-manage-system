from notifications.signals import notify
from django.contrib.auth.models import User,Group
from django.db.models import Q




def send_notification(sender,target,verb):
    if not sender.is_superuser:
        notify.send(
            sender,
            recipient=User.objects.filter(Q(is_superuser=True) | Q(is_staff=True)).exclude(pk=sender.pk),
            verb=verb,
            target=target,
            )


def send_notification_to_user(sender, recipient, target, verb):
    """向指定用户发送通知（如管理员通知借阅者）"""
    if recipient:
        notify.send(
            sender,
            recipient=recipient,
            verb=verb,
            target=target,
        )