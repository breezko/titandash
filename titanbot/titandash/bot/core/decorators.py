"""
decorators.py

Any decorators used by the bot should be placed here. Mostly used to store the _not_in_transition decorator
that handles pausing the bot and fixing any issues that may come up when a transition state is detected.

A transition state refers to one of the following states in game:
    - Stage changing over (screen overlay present during).
    - Premium ad available (no way to click out of this other than accepting/declining).

These states are handled through clicking on the top of the screen if required. The ad collection
is handled manually by clicking on either accept or decline based on user settings.
"""
from functools import wraps

from .utilities import in_transition_func, sleep
from random import randint


# Globally available properties dictionary, store information about functions
# and their options within the app. See "BotProperty" below.
_PROPERTIES = dict()


class BotProperty(object):
    """
    Queueable Function Decorator.
    """
    def __init__(self, queueable=False, forceable=False, shortcut=None, tooltip=None, interval=None):
        """
        Initialize the queueable decorator on a function, we should be able to choose
        a couple of options when making a function queueable, including whether ot not it
        is a function that should be "forced", the shortcut used and the tooltip displayed.

        :param queueable: Should this function be a queueable that can be queued by the bot.
        :param forceable: Should this function be forceable when called by the bot.
        :param shortcut: Specify a keyboard shortcut that can be used to queue the function.
        :param tooltip:  Specify a tooltip that will be displayed when the function is hovered over.
        :param interval: Specify an interval that will be used to derive scheduled function periods.
        """
        self.queueable = queueable
        self.forceable = forceable
        self.shortcut = shortcut
        self.tooltip = tooltip
        self.interval = interval

    def __call__(self, function):
        """
        Perform the magic required when this decorator is applied to our
        functions here. Ensuring that the function is present in the our
        properties dictionary.
        """
        self._add_property(
            function=function
        )

        def wrapper(*args, **kwargs):
            # Run our function normally once we've added it to our
            # globally available queueable dictionary.
            return function(*args, **kwargs)

        # Returning wrapper function here, retain class decorator norms.
        return wrapper

    def _add_property(self, function):
        """
        Add the current function to the properties global variable with it's settings included.
        """
        if function.__name__ not in _PROPERTIES:
            _PROPERTIES[function.__name__] = {
                'name': function.__name__,
                'function': function,
                'queueable': self.queueable,
                'forceable': self.forceable,
                'shortcut': self.shortcut,
                'tooltip': self.tooltip,
                'interval': self.interval
            }

    @classmethod
    def _all(cls, function=None, queueables=False, forceables=False, shortcuts=False, intervals=False):
        """
        Utility function that attempts to grab all of the properties based on the options
        specified, we can return the information for a specific function, or return all properties
        with specific information associated with them.
        """
        _all = {}
        results = []

        if function:
            _all.update(_PROPERTIES[function])
        else:
            _all.update(_PROPERTIES)

        for prop in _all.values():
            if shortcuts and prop["shortcut"]:
                results.append(prop)
                continue
            if queueables and prop["queueable"]:
                results.append(prop)
                continue
            if forceables and prop["forceable"]:
                results.append(prop)
                continue
            if intervals and prop["interval"]:
                results.append(prop)
                continue

        return results

    @classmethod
    def all(cls, function=None):
        return cls._all(function=function, queueables=True, forceables=True, shortcuts=True)

    @classmethod
    def queueables(cls, function=None):
        return cls._all(function=function, queueables=True)

    @classmethod
    def forceables(cls, function=None):
        return cls._all(function=function, forceables=True)

    @classmethod
    def shortcuts(cls, function=None):
        return cls._all(function=function, shortcuts=True)

    @classmethod
    def intervals(cls, function=None):
        return cls._all(function=function, intervals=True)


def not_in_transition(function, max_loops=30):
    """
    Stop functionality until some sort of game object is on the screen that represents the game not being
    in a transition state. If a transition state is detected, click the top of the screen a couple of
    times.

    We will provide a max amount of loops before giving up and attempting to continue with bot functionality.

    Note, this is used as a decorator function, placed above functions to ensure that the in_transition_func is called
    before the actual function is called. in_transition_func can be called directly if needed in specific
    parts of the bot.
    """
    @wraps(function)
    def in_transition(*args, **kwargs):
        """Looping until a transition state is no longer found. Or max loops has been reached."""
        in_transition_func(*args, max_loops=max_loops)
        return function(*args, **kwargs)
    return in_transition


def wait_afterwards(function, floor, ceiling):
    """
    Delay a function after it's been called for a random amount of seconds between the specified floor and ceiling.
    """
    def wrapped(*args, **kwargs):
        function(*args, **kwargs)
        sleep(randint(floor, ceiling))
    return wrapped


def wrap_current_function(function):
    """
    Wrap the decorated function to allow for property updates used with the live dashboard.

    This allows the current function display to change based on the function being executed.
    """
    def current_function(*args, **kwargs):
        args[0].props.current_function = function.__name__
        return function(*args, **kwargs)
    return current_function
