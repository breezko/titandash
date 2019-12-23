from titanauth.models.user_reference import ExternalAuthReference
from titanauth.authentication.constants import (
    AUTH_AUTHENTICATE_URL, AUTH_STATE_URL, AUTH_RELEASE_URL
)

import requests


class AuthWrapper(object):
    def __init__(self):
        """
        Initialize new AuthWrapper object.
        """
        self.reference = ExternalAuthReference.objects.first()

    def authenticate(self):
        """
        Attempt to authenticate a specified set of credentials against the external backend.

        If no credentials are specified, an attempt is made to use the user reference if one is available.
        """
        # Fire a request off to the external backend, to determine if the information present
        # exists and is valid within the system.
        return requests.post(
            url=AUTH_AUTHENTICATE_URL,
            data={
                "email": self.reference.email,
                "token": self.reference.token
            }
        )

    def _state(self, state):
        if not self.reference.valid:
            raise ValueError("Authentication reference: {ref} is invalid.".format(ref=self.reference))

        return requests.post(
            url=AUTH_STATE_URL,
            data={
                "email": self.reference.email,
                "token": self.reference.token,
                "state": state,
            }
        )

    def offline(self):
        """
        Attempt to set the current authentication wrapper to an offline state.
        """
        return self._state(state="offline")

    def online(self):
        """
        Attempt to set the current authentication reference to an online state.
        """
        return self._state(state="online")

    def release_information(self, version):
        """
        Retrieve the version information for the specified version.
        """
        if not self.reference.valid:
            raise ValueError("Authentication reference: {ref} is invalid.".format(ref=self.reference))

        return requests.get(
            url=AUTH_RELEASE_URL,
            params={
                "version": version
            }
        ).json()
