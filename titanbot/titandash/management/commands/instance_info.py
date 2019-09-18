from django.core.management.base import BaseCommand

from titandash.models.bot import BotInstance
from titandash.models.configuration import Configuration
from titandash.utils import WindowHandler
from titandash.bot.core.constants import WINDOW_FILTER

import json


class Command(BaseCommand):
    """
    Custom management command used to grab all information needed to initialize a new bot session.
    """
    help = "Grab all available configurations separated by commas."

    def handle(self, *args, **options):
        # Grab all information required for instance initiation.
        # Windows, Instances, Configurations.
        handler = WindowHandler()
        handler.enum()

        # Grab any windows that are currently open and active.
        windows = handler.filter(contains=WINDOW_FILTER)
        windows = [windows[w].text for w in windows]

        # Instances and configurations.
        instances = [b.name for b in BotInstance.objects.all()]
        configurations = [c.name for c in Configuration.objects.all()]

        return json.dumps({
            "windows": windows,
            "instances": instances,
            "configurations": configurations
        })
