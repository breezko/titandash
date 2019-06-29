from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/instance/$', consumers.BotInstanceConsumer),
    url(r'^ws/log/$', consumers.LogRecordConsumer),
    url(r'^ws/prestige/$', consumers.PrestigeConsumer),
    url(r'^ws/queued/$', consumers.QueuedFunctionConsumer),
]
