from django.core.management.base import BaseCommand

from settings import BOT_VERSION


class Command(BaseCommand):
    """
    Custom management command used to grab the current bot version.
    """
    help = "Grab current project version."

    def handle(self, *args, **options):
        return BOT_VERSION
