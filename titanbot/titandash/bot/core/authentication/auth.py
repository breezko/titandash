"""
auth.py

Controls the authentication process that takes place when bootstrapping a new BotInstance.

When a Bot is initialized, an authentication Token is required that will be used to validate
the instance.

Multiple routes could happen during authentication... They are as follows:

    - No AuthToken Model available.
    - AuthToken is already active.
    - AuthToken has expired.

The type of token grabbed will also modify functionality slightly... A Premium, or development token will never
become expired, and the functionality here can reflect that when grabbing the boolean.
"""
from django.conf import settings
from django.utils.timezone import now

from titandash.bot.core.authentication import exceptions
from titandash.bot.core.authentication.constants import (
    TOKENS_URI, DATE_FMT, BASIC
)

from datetime import datetime

import requests


class Authenticator:
    """Main Authenticator Class."""
    def __init__(self, token, tooled=False):
        """Begin authentication through class initializer."""
        self.token = token
        self.headers = self._build_header()
        self.endpoints = self._build_endpoints()

        # "tooled" means we only want to access the authenticator to make
        # requests to the given token... (ie: Termination).
        if tooled:
            return

        # Get actual token instance.
        self.instance = self.retrieve()

        if "detail" in self.instance:
            raise exceptions.RetrievalException("Token could not be retrieved: {detail}... Is your token setup properly?".format(detail=self.instance))

        if self.active():
            raise exceptions.AlreadyActiveException("Token: <{token}> is already active.".format(token=self.token))
        if self.expired():
            raise exceptions.TokenExpiredException("Token: <{token}> is currently expired.".format(token=self.token))

        # Base possible exceptions are passed at this point, attempt to
        # activate the token.
        try:
            response = self.activate()
            assert response["status"] == "active"
        # Catch all here and raise an ActivationException.
        except Exception:
            raise exceptions.ActivationException("An error occurred while activating token: <{token}>".format(token=self.token))

    def _build_header(self):
        """Build the custom headers that will be attached to any web requests that are made."""
        return {
            "Authorization": "{secret_key} {secret_value} {token_key} {token_value}".format(
                secret_key=settings.SECRET_BOT_KEY, secret_value=settings.SECRET_BOT_VALUE,
                token_key=settings.TOKEN_KEY, token_value=self.token
            )
        }

    def _build_endpoints(self):
        return {
            "retrieve": TOKENS_URI + self.token + "/",
            "activate": TOKENS_URI + self.token + "/activate/",
            "terminate": TOKENS_URI + self.token + "/terminate/"
        }

    def _request(self, method, url):
        """Generic request handler."""
        req = getattr(requests, method, None)
        if req is None:
            raise exceptions.InvalidMethodError(
                "The request method {method} does not exist in the request library.".format(method=method))

        # Method exists... Send request out from here.
        return req(url=url, headers=self.headers).json()

    def active(self):
        return self.instance["active"] is True

    def expired(self):
        if self.instance["type"] == BASIC:
            return datetime.strptime(self.instance["expires"], DATE_FMT) <= now()
        else:
            return False

    def retrieve(self):
        """Attempt to retrieve the current token instance."""
        return self._request("get", self.endpoints["retrieve"])

    def activate(self):
        """Attempt to send an activation request to the current token instance."""
        return self._request("get", self.endpoints["activate"])

    def terminate(self):
        """Attempt to send a termination request to the current token instance."""
        return self._request("get", self.endpoints["terminate"])
