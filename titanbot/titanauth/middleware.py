"""
middleware.py

Store any middleware classes/functions related directly to the external authentication
that is used to ensure only valid users can access the dashboard.
"""
from django.shortcuts import redirect

from titanauth.models.user_reference import ExternalAuthReference


class TitandashAuthenticationMiddleware:
    """
    TitandashAuthenticationMiddleware is used to send requests to the external authentication
    backend to determine if a user has access to the dashboard.
    """
    def __init__(self, get_response):
        self.exceptions = [
            "/auth/authenticate",
            "/auth/ajax/credentials",

            # Bootstrapper urls should be allowed into our pages always.
            # When bootstrapping is finished, if no authentication has been
            # done, then we can force the login through our middleware.
            "/bootstrap/",
            "/bootstrap/ajax/check_update",
            "/bootstrap/ajax/perform_update",
            "/bootstrap/ajax/perform_requirements",
            "/bootstrap/ajax/perform_node_packages",
            "/bootstrap/ajax/perform_migration",
            "/bootstrap/ajax/perform_cache",
            "/bootstrap/ajax/perform_static",
            "/bootstrap/ajax/perform_dependency",
        ]
        self.get_response = get_response

    def __call__(self, request):
        """
        Code executed for each request before the view (and later middleware) is called.
        """
        # No user has been set yet, redirect to the login page and setup an empty user
        # that will be used for any subsequent requests.
        if request.path not in self.exceptions:
            if not ExternalAuthReference.objects.valid():
                return redirect("authenticate")

        # Grabbing and returning the response using the default django get_response
        # implementation.
        return self.get_response(request)
