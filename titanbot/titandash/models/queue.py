from django.db import models

from channels.generic.websocket import async_to_sync
from channels.layers import get_channel_layer

from titandash.constants import DATETIME_FMT


HELP_TEXT = {
    "function": "Name of the function you would like to execute as soon as possible.",
    "created": "When was this queue instance generated.",
}


class QueueManager(models.Manager):
    def add(self, function):
        """Add the specified function to the function queue."""
        return self.create(function=function)


class Queue(models.Model):
    """
    Queue Model.

    Simple model used by a Bot Session to perform functions directly without the need to wait.

    Functions are performed once per game loop and may take a bit to be executed. Functions will be executed
    from oldest to newest in order.

    The function field represents the name of an actual function provided by the Bot.
    """
    class Meta:
        verbose_name = "Queued Function"
        verbose_name_plural = "Queued Functions"

    objects = QueueManager()
    function = models.CharField(verbose_name="Function", max_length=255, help_text=HELP_TEXT["function"])
    created = models.DateTimeField(verbose_name="Created", auto_now_add=True, help_text=HELP_TEXT["created"])

    def __str__(self):
        from titandash.utils import title
        return "Queued: {function}".format(function=title(self.function))

    def save(self, *args, **kwargs):
        super(Queue, self).save(*args, **kwargs)

        # Channels send websocket message.
        channel_layer = get_channel_layer()
        group_name = "titan_queued"
        queued = self.json()

        async_to_sync(channel_layer.group_send)(
            group_name, {
                "type": "saved",
                "queued": queued
            }
        )

    def json(self):
        """Convert the QueuedFunction into a JSON compliant dictionary."""
        from titandash.utils import title
        return {
            "id": self.pk,
            "function": self.function,
            "title": title(self.function),
            "created": self.created.strftime(DATETIME_FMT)
        }

    def latest(self):
        """Retrieve a list of the latest queued functions."""
        lst = []
        for queue in self.objects.all().order_by("-created"):
            lst.append(queue.json())

        return lst

    def finish(self):
        """
        When a queued function is executed, we can call the finish method to send a signal
        to out WebSocket to let us know it's been removed.
        """
        # Channels send websocket message.
        channel_layer = get_channel_layer()
        group_name = "titan_queued"
        queued = self.json()

        # Send message to group.
        async_to_sync(channel_layer.group_send)(
            group_name, {
                "type": "finished",
                "queued": queued
            }
        )

        # Delete the queued function after websocket message is sent.
        self.delete()

    @classmethod
    def flush(cls):
        cls.objects.all().delete()
