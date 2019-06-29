from .models.bot import BotInstance
from .constants import RUNNING, PAUSED, STOPPED

from titandash.models.configuration import Configuration
from titandash.models.queue import Queue
from titandash.bot.core.bot import Bot

from threading import Thread

import time
import string


def title(value):
    """Remove underscored and replace with spaces. Apply 'title' modification to value."""
    capped = [char for char in string.capwords(value.replace("_", " "))]

    # If a string also contains some letters after an apostrophe, we should capitalize that
    # letter... (ie: O'ryan's Charm -> O'Ryan's Charm).
    for index, char in enumerate(capped):
        if char is "'":
            if index + 1 <= len(capped):
                if capped[index + 2] != ' ':
                    capped[index + 1] = capped[index + 1].upper()

    return "".join(capped)


def start(config):
    """
    Start a new Bot Process if one does not already exist. We can check for an existing one by looking at the
    current Bot model and the data present. If one does exist, we can send a termination signal to ensure that
    the old bot has stopped and that a new Bot Session can be initialized.
    """
    instance = BotInstance.objects.grab()

    if instance.state == RUNNING:
        Queue.objects.add(function="terminate")
    if instance.state == PAUSED:
        Queue.objects.add(function="resume")

    while instance.state != STOPPED:
        time.sleep(0.2)
        instance = BotInstance.objects.grab()
        continue

    # At this point. The bot is no longer running, and a new instance can be started up
    # in a new thread.
    # Bot initialization will handle the creation of a new BotInstance.
    if instance.state == STOPPED:
        Thread(target=Bot, kwargs={'configuration': Configuration.objects.get(pk=config), 'start': True}).start()


def pause():
    """Attempt to pause the current BotInstance if it is currently running."""
    instance = BotInstance.objects.grab()
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="pause")


def stop():
    """Attempt to stop the current BotInstance if it is currently running."""
    instance = BotInstance.objects.grab()
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="terminate")


def resume():
    """Attempt to resume the current BotInstance if it is currently running."""
    instance = BotInstance.objects.grab()
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="resume")
