"""
constants.py

Store constants relating to the external authentication backend.
"""

# Base urls.
AUTH_BASE_URL = "https://titandash.net"
AUTH_API_URL = "/api"

# Endpoints.
AUTH_AUTHENTICATE_ENDPOINT = "/authenticate"
AUTH_STATE_ENDPOINT = "/state"
AUTH_SIGNUP_ENDPOINT = "/auth/register"
AUTH_ACCOUNT_ENDPOINT = "/account"
AUTH_RELEASE_ENDPOINT = "/release"

# Urls.
AUTH_AUTHENTICATE_URL = "{base}{api}{authenticate}".format(base=AUTH_BASE_URL, api=AUTH_API_URL, authenticate=AUTH_AUTHENTICATE_ENDPOINT)
AUTH_STATE_URL = "{base}{api}{state}".format(base=AUTH_BASE_URL, api=AUTH_API_URL, state=AUTH_STATE_ENDPOINT)
AUTH_SIGNUP_URL = "{base}{signup}".format(base=AUTH_BASE_URL, signup=AUTH_SIGNUP_ENDPOINT)
AUTH_ACCOUNT_URL = "{base}{account}".format(base=AUTH_BASE_URL, account=AUTH_ACCOUNT_ENDPOINT)
AUTH_RELEASE_URL = "{base}{api}{release}".format(base=AUTH_BASE_URL, api=AUTH_API_URL, release=AUTH_RELEASE_ENDPOINT)
