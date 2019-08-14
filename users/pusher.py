import pusher
from django.conf import settings


def connect():
    return pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_API_KEY,
        secret=settings.PUSHER_SECRET_KEY,
        cluster=settings.PUSHER_CLUSTER,
        ssl=settings.PUSHER_SSL
    )