from django.core.management.base import BaseCommand

from titandash.models.bot import BotInstance

import json


class Command(BaseCommand):
    """
    Custom management command used to grab all active bot instances.
    """
    help = "Grab all active bot instances."

    def handle(self, *args, **options):
        return json.dumps({
            "instances": [b.name for b in BotInstance.objects.filter(state__in=["running", "paused"])]
        })
