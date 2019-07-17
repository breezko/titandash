from django.db import models
from django.utils import timezone
from django.conf import settings

from channels.generic.websocket import async_to_sync
from channels.layers import get_channel_layer

from titandash.constants import RUNNING, PAUSED, STOPPED, DATETIME_FMT
from titandash.models.statistics import Statistics, Log
from titandash.models.queue import Queue


BOT_STATE_CHOICES = (
    ("running", "RUNNING"),
    ("paused", "PAUSED"),
    ("stopped", "STOPPED")
)

BOT_HELP_TEXT = {
    "state": "Current state of the bot.",
    "uuid": "Unique identifier for this bot instance.",
    "session": "Session associated with the current bot instance.",
    "started": "The date that the bot was started.",
    "current_function": "The current function being executed by the bot."
}


class BotInstanceManager(models.Manager):
    def grab(self):
        """
        Attempt to grab the current Bot instance. We only ever want one single instance. If one does not exist,
        we generate a new one with some default values.
        """
        if len(self.all()) == 0:
            self.create()

        # Returning the existing instance.
        return self.all().first()


class BotInstance(models.Model):
    """
    Bot Model.

    This model is only used to store and check that the bot is currently running or not.

    The state of the bot will be updated by the Bot instance itself when one is started. Additionally,
    if the bot is stopped or shutdown manually (no crash). The bot instance in the database will be updated.

    If the bot hard crashes somehow, we also do a check to see if the PID running the bot that was present
    last is still present and running on the local machine running the bot.
    """
    class Meta:
        verbose_name = "Bot Instance"
        verbose_name_plural = "Bot Instances"

    objects = BotInstanceManager()
    state = models.CharField(verbose_name="State", choices=BOT_STATE_CHOICES, default=STOPPED, max_length=255, help_text=BOT_HELP_TEXT["state"])
    session = models.ForeignKey(verbose_name="Session", blank=True, null=True, to="Session", on_delete=models.CASCADE, help_text=BOT_HELP_TEXT["session"])
    started = models.DateTimeField(verbose_name="Started", blank=True, null=True, help_text=BOT_HELP_TEXT["started"])
    current_function = models.CharField(verbose_name="Current Function", max_length=255, blank=True, null=True, help_text=BOT_HELP_TEXT["current_function"])

    # Bot Variables...
    configuration = models.ForeignKey(verbose_name="Current Configuration", to="Configuration", blank=True, null=True, on_delete=models.CASCADE)
    log = models.ForeignKey(verbose_name="Current Log", to=Log, on_delete=models.CASCADE, blank=True, null=True)
    current_stage = models.PositiveIntegerField(verbose_name="Current Stage", blank=True, null=True)
    next_action_run = models.DateTimeField(verbose_name="Next Action Run", blank=True, null=True)
    next_prestige = models.DateTimeField(verbose_name="Next Timed Prestige", blank=True, null=True)
    next_stats_update = models.DateTimeField(verbose_name="Next Stats Update", blank=True, null=True)
    next_recovery_reset = models.DateTimeField(verbose_name="Next Recovery Reset", blank=True, null=True)
    next_daily_achievement_check = models.DateTimeField(verbose_name="Next Daily Achievement Check", blank=True, null=True)
    next_heavenly_strike = models.DateTimeField(verbose_name="Next Heavenly Strike", blank=True, null=True)
    next_deadly_strike = models.DateTimeField(verbose_name="Next Deadly Strike", blank=True, null=True)
    next_hand_of_midas = models.DateTimeField(verbose_name="Next Hand Of Midas", blank=True, null=True)
    next_fire_sword = models.DateTimeField(verbose_name="Next Fire Sword", blank=True, null=True)
    next_war_cry = models.DateTimeField(verbose_name="Next War Cry", blank=True, null=True)
    next_shadow_clone = models.DateTimeField(verbose_name="Next Shadow Clone", blank=True, null=True)
    next_artifact_upgrade = models.CharField(verbose_name="Next Artifact Upgrade", max_length=255, blank=True, null=True)

    def __str__(self):
        return "BotInstance [{state}]".format(state=self.state.upper())

    def save(self, *args, **kwargs):
        super(BotInstance, self).save(*args, **kwargs)

        # Channels send websocket message.
        channel_layer = get_channel_layer()
        group_name = 'titan_instance'
        instance = self.json()

        # Send message to group.
        async_to_sync(channel_layer.group_send)(
            group_name, {
                'type': 'saved',
                'instance': instance
            }
        )

    def get_diff_from_max_stage(self, percent=False):
        if self.current_stage is None or self.current_stage == "":
            return None

        stats = Statistics.objects.grab()

        try:
            stage = int(self.current_stage)
        except ValueError:
            return None

        max_stage = stats.game_statistics.highest_stage()
        if max_stage is None:
            return None

        if not percent:
            return int(max_stage - stage)

        if max_stage == stage:
            return "100%"

        return "{:.2%}".format(float(stage) / max_stage)

    def json(self):
        """Convert the BotInstance into a JSON compliant dictionary."""
        from django.urls import reverse
        from titandash.utils import title
        from titandash.models.artifact import Artifact
        dct = {
            "state": self.state.upper(),
            "started": {
                "datetime": str(self.started) if self.started else None,
                "formatted": self.started.astimezone().strftime(DATETIME_FMT) if self.started else None
            },
            "current_function": self.current_function,
            "log_file": reverse('log', kwargs={'pk': self.log.pk}) if self.log else "N/A",
            "current_stage": {
                "stage": self.current_stage,
                "diff_from_max": self.get_diff_from_max_stage(),
                "percent_from_max": self.get_diff_from_max_stage(percent=True)
            },
            "next_artifact_upgrade": {
                "title": title(self.next_artifact_upgrade) if self.next_artifact_upgrade else None,
                "image": "{dir}{path}".format(dir=settings.STATIC_URL, path=Artifact.objects.get(name=self.next_artifact_upgrade).image) if self.next_artifact_upgrade else None
            },
            "next_action_run": {
                "datetime": str(self.next_action_run) if self.next_action_run else None,
                "formatted": self.next_action_run.astimezone().strftime(DATETIME_FMT) if self.next_action_run else None
            },
            "next_prestige": {
                "datetime": str(self.next_prestige) if self.next_prestige else None,
                "formatted": self.next_prestige.astimezone().strftime(DATETIME_FMT) if self.next_prestige else None
            },
            "next_stats_update": {
                "datetime": str(self.next_stats_update) if self.next_stats_update else None,
                "formatted": self.next_stats_update.astimezone().strftime(DATETIME_FMT) if self.next_stats_update else None
            },
            "next_recovery_reset": {
                "datetime": str(self.next_recovery_reset) if self.next_recovery_reset else None,
                "formatted": self.next_recovery_reset.astimezone().strftime(DATETIME_FMT) if self.next_recovery_reset else None
            },
            "next_daily_achievement_check": {
                "datetime": str(self.next_daily_achievement_check) if self.next_daily_achievement_check else None,
                "formatted": self.next_daily_achievement_check.astimezone().strftime(DATETIME_FMT) if self.next_daily_achievement_check else None
            },
            "next_heavenly_strike": {
                "datetime": str(self.next_heavenly_strike) if self.next_heavenly_strike else None,
                "formatted": self.next_heavenly_strike.astimezone().strftime(DATETIME_FMT) if self.next_heavenly_strike else None
            },
            "next_deadly_strike": {
                "datetime": str(self.next_deadly_strike) if self.next_deadly_strike else None,
                "formatted": self.next_deadly_strike.astimezone().strftime(DATETIME_FMT) if self.next_deadly_strike else None
            },
            "next_hand_of_midas": {
                "datetime": str(self.next_hand_of_midas) if self.next_hand_of_midas else None,
                "formatted": self.next_hand_of_midas.astimezone().strftime(DATETIME_FMT) if self.next_hand_of_midas else None
            },
            "next_fire_sword": {
                "datetime": str(self.next_fire_sword) if self.next_fire_sword else None,
                "formatted": self.next_fire_sword.astimezone().strftime(DATETIME_FMT) if self.next_fire_sword else None
            },
            "next_war_cry": {
                "datetime": str(self.next_war_cry) if self.next_war_cry else None,
                "formatted": self.next_war_cry.astimezone().strftime(DATETIME_FMT) if self.next_war_cry else None
            },
            "next_shadow_clone": {
                "datetime": str(self.next_shadow_clone) if self.next_shadow_clone else None,
                "formatted": self.next_shadow_clone.astimezone().strftime(DATETIME_FMT) if self.next_shadow_clone else None
            }
        }

        if self.session:
            dct["session"] = {
                "url": reverse('session', kwargs={"uuid": self.session.uuid}),
                "uuid": self.session.uuid
            }
        if self.configuration:
            dct["configuration"] = {
                "url": reverse("admin:titandash_configuration_change", kwargs={"object_id": self.configuration.pk}),
                "name": self.configuration.name
            }

        return dct

    def reset_vars(self):
        self.current_function = None
        self.configuration = None
        self.log_file = None
        self.current_stage = None
        self.next_action_run = None
        self.next_prestige = None
        self.next_stats_update = None
        self.next_recovery_reset = None
        self.next_daily_achievement_check = None
        self.next_deadly_strike = None
        self.next_hand_of_midas = None
        self.next_fire_sword = None
        self.next_war_cry = None
        self.next_shadow_clone = None
        self.upgrade_artifacts = None
        self.next_artifact_upgrade = None

    def start(self, session):
        """Start the BotInstance. Should be called when the Bot is first initialized."""
        self.state = RUNNING
        self.session = session
        self.started = timezone.now()
        self.current_function = "INITIALIZING..."
        self.save()

    def pause(self):
        """Pause the BotInstance. Called when signal is sent from user."""
        self.state = PAUSED
        self.current_function = "PAUSED..."
        self.save()

    def stop(self):
        """Stop and kill the BotInstance. Called when exception is raised or manual termination by user."""
        self.state = STOPPED
        self.session = None
        self.started = None
        self.current_function = None
        self.reset_vars()
        self.save()

        # Additionally, flush the QueuedFunctions list just to be sure.
        Queue.flush()

    def resume(self):
        """Resume the BotInstance. Called when resumed from a paused state."""
        self.state = RUNNING
        self.save()
