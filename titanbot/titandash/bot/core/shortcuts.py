"""
shortcuts.py

Encapsulating the threading functionality that is used by the keyboard shortcuts present
within the Bot. Used to ensure the Thread is stoppable while still using our
while True loop to always be waiting for I/O.
"""
from django.utils import timezone

from titandash.models.queue import Queue
from titandash.bot.core.constants import FUNCTION_SHORTCUTS, SHORTCUT_FUNCTIONS

import operator
import collections
import datetime


SHIFT = "shift"
CTRL = "ctrl"
ALT = "alt"


class ShortcutListener:
    def __init__(self, logger, instance, cooldown=2):
        self.logger = logger
        self.instance = instance
        self.cooldown = cooldown

        # Using timestamp and resume variables to block after a shortcut
        # is pressed so the same function isn't queued up twice.
        self.timestamp = timezone.now()
        self.resume = timezone.now()

        # Current is used to determine active modifiers/key presses.
        self.current = dict()
        self.index = 0

    @staticmethod
    def _fix_event(event):
        """
        Fix the event so that any shift, ctrl or alt buttons can be used to initiate a combo.
        """
        split = event.name.split(" ")[-1]
        if split in [SHIFT, CTRL, ALT]:
            return split

        return event.name

    def on_press(self, event):
        """
        When a keypress takes place, some checks take place to fixup the event passed and additional checks
        are present to allow a user to use keyboard combinations to activate functionality within a Bot.
        """
        self.timestamp = timezone.now()

        if self.index < 0:
            self.index = 0
        if event:
            key = self._fix_event(event=event)
            if key in self.current:
                return

            # Determine if the key pressed is present in any of the available shortcuts.
            for short in FUNCTION_SHORTCUTS.keys():
                if key in short.split("+"):
                    self.current[key] = self.index
                    self.index += 1
                    break

            if len(self.current) > 0:
                combo = "+".join(collections.OrderedDict(sorted(self.current.items(), key=operator.itemgetter(1))).keys())
                if combo in FUNCTION_SHORTCUTS:
                    if self.timestamp > self.resume:
                        Queue.objects.add(function=FUNCTION_SHORTCUTS[combo], instance=self.instance)
                        self.logger.debug("{combo} pressed, executing '{func}'".format(combo=combo, func=SHORTCUT_FUNCTIONS[FUNCTION_SHORTCUTS[combo]]))
                        self.resume = self.resume + datetime.timedelta(seconds=1)

    def on_release(self, event):
        """When a keypress is released, removing that key from the current set of active keys."""
        try:
            self.current.pop(self._fix_event(event=event))
            self.index -= 1
        except KeyError:
            pass
