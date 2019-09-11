from titanauth.models.user_reference import ExternalAuthReference
from titanauth.authentication.constants import AUTH_ACCOUNT_URL


def login(request):
    """
    Include the current external auth reference in template contexts.

    """
    return {
        "auth": ExternalAuthReference.objects.all().first(),
        "auth_account": AUTH_ACCOUNT_URL
    }
