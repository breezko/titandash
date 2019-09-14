from django.core.management.base import BaseCommand, CommandError

from titanauth.models.user_reference import ExternalAuthReference
from titanauth.authentication.wrapper import AuthWrapper


class Command(BaseCommand):
    """
    Custom management command used to send offline state changes through an external process.
    """
    help = "Sets the current external authentication reference to offline."

    def handle(self, *args, **options):
        if ExternalAuthReference.objects.valid():
            AuthWrapper().offline()
        else:
            raise CommandError("ExternalAuthReference is not valid.")
