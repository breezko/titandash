from django.db import models

from titandash.constants import DATETIME_FMT

from channels.generic.websocket import async_to_sync
from channels.layers import get_channel_layer


HELP_TEXT = {
    "timestamp": "Timestamp representing when this prestige took place.",
    "time": "The time/duration of the prestige.",
    "stage": "The stage that was reached when the prestige took place.",
    "artifact": "The artifact upgraded following this prestige.",
    "session": "The session associated with this prestige."
}


class Prestige(models.Model):
    """
    Prestige Model.

    Store all prestiges in the database and some associated information for statistical purposes.
    """
    class Meta:
        verbose_name = "Prestige"
        verbose_name_plural = "Prestiges"

    timestamp = models.DateTimeField(verbose_name="Timestamp", auto_now_add=True, help_text=HELP_TEXT["timestamp"])
    time = models.DurationField(verbose_name="Duration", blank=True, null=True, help_text=HELP_TEXT["time"])
    stage = models.PositiveIntegerField(verbose_name="Stage", blank=True, null=True, help_text=HELP_TEXT["stage"])
    artifact = models.ForeignKey(verbose_name="Artifact Upgraded", to="Artifact", on_delete=models.CASCADE, help_text=HELP_TEXT["artifact"])
    session = models.ForeignKey(verbose_name="Session", to="Session", on_delete=models.CASCADE, help_text=HELP_TEXT["session"])

    def __str__(self):
        return "Prestige [{stage} - {time}]".format(stage=self.stage, time=self.time)

    def json(self):
        from django.urls import reverse
        return {
            "timestamp": {
                "datetime": str(self.timestamp),
                "formatted": self.timestamp.astimezone().strftime(DATETIME_FMT),
                "epoch": int(self.timestamp.timestamp())
            },
            "duration": {
                "formatted": str(self.time) if self.time else "N/A",
                "seconds": self.time.total_seconds() if self.time else "N/A"
            },
            "artifact": self.artifact.json(),
            "stage": self.stage if self.stage else "N/A",
            "session": {
                "uuid": self.session.uuid,
                "uuid_short": self.session.uuid[:8] + "...",
                "url": reverse('session', kwargs={"uuid": self.session.uuid}),
            }
        }

    def save(self, *args, **kwargs):
        super(Prestige, self).save(*args, **kwargs)

        # Channels and websocket message.
        channel_layer = get_channel_layer()
        group_name = "titan_prestige"
        prestige = self.json()

        async_to_sync(channel_layer.group_send)(
            group_name, {
                "type": "saved",
                "prestige": prestige
            }
        )
