"""
exceptions.py

Any exceptions related directly to the authentication may be placed here.
"""


class InvalidMethodError(Exception):
    """If the method specified on the request does not exist within the request library."""
    pass


class AlreadyActiveException(Exception):
    """If the token specified to be activated is already active."""
    pass


class TokenExpiredException(Exception):
    """Token has expired."""
    pass


class RetrievalException(Exception):
    """If for some reason a Token Instance can not be retrieved, generic exception handler."""
    pass


class ActivationException(Exception):
    """If the activation of a token fails for some reason, this catch all exception can handle it."""
    pass
