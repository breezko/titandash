from django.core.management.base import BaseCommand
from django.urls import reverse

from titandash.models.bot import BotInstance
from titandash.models.configuration import Configuration
from titandash.utils import start, WindowHandler
from titandash.bot.core.constants import WINDOW_FILTER

import requests
import json


class Command(BaseCommand):
    """
    Custom management command used to initiate a new bot session.
    """
    help = "Grab all available configurations separated by commas."

    def add_arguments(self, parser):
        parser.add_argument("window", type=str)
        parser.add_argument("instance", type=str)
        parser.add_argument("configuration", type=str)

    def handle(self, window, instance, configuration, *args, **options):
        """
        Note that our arguments come in as the names of them as strings.

        :param window: Name of window being used.
        :param instance: Name of instance being used.
        :param configuration:  Name of configuration being used.
        """
        # Grab all information required for instance initiation.
        # Windows, Instances, Configurations.
        handler = WindowHandler()
        handler.enum()

        # Grab any windows that are currently open and active.
        windows = handler.filter(contains=WINDOW_FILTER)

        chosen_window = None
        for w in windows:
            if windows[w].text == window:
                chosen_window = windows[w].hwnd

        # If the chosen window is no longer open, likely closed in between gui
        # submit, and the command execution.
        if not chosen_window:
            return "Window Chosen Not Found"

        instance = BotInstance.objects.get(name=instance)
        configuration = Configuration.objects.get(name=configuration).pk

        response = json.loads(
            requests.get(
                url="http://localhost:8000" + reverse("signal"),
                params={
                    "instance": instance.pk,
                    "signal": "PLAY",
                    "config": configuration,
                    "window": chosen_window
                }
            ).content
        )

        # BotInstance already running?
        if response["status"] != "success":
            return response["message"].title()
        # Waiting until the session has been started.
        while instance.session is None:
            instance.refresh_from_db()

        return "Session %s Started" % instance.session.uuid
