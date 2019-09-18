from django.core.management.base import BaseCommand
from django.urls import reverse

from titandash.models.bot import BotInstance

import requests
import json


class Command(BaseCommand):
    """
    Custom management command used to initiate a new bot session.
    """
    help = "Kill an existing instance that's currently active."

    def add_arguments(self, parser):
        parser.add_argument("instance", type=str)

    def handle(self, instance, *args, **options):
        """
        Note that our arguments come in as the names of them as strings.

        :param instance: Name of instance being killed.
        """
        instance = BotInstance.objects.get(name=instance)

        response = json.loads(
            requests.get(
                url="http://localhost:8000" + reverse("kill_instance"),
                params={
                    "instance": instance.pk
                }
            ).content
        )

        if response["killed"]:
            return "{instance} Successfully Killed".format(instance=instance.name)
        else:
            return "BotInstance Not Running"
