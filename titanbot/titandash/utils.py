from .constants import *

from titandash.models.queue import Queue
from titandash.bot.core.bot import Bot

from threading import Thread

import win32gui
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


def start(config, window, instance):
    """
    Start a new Bot Process if one does not already exist. We can check for an existing one by looking at the
    current Bot model and the data present. If one does exist, we can send a termination signal to ensure that
    the old bot has stopped and that a new Bot Session can be initialized.
    """
    from titandash.models.configuration import Configuration

    if instance.state == RUNNING:
        Queue.objects.add(function="terminate", instance=instance)
    if instance.state == PAUSED:
        Queue.objects.add(function="resume", instance=instance)

    while instance.state != STOPPED:
        time.sleep(0.2)
        instance = instance.refresh_from_db()
        continue

    # At this point. The bot is no longer running, and a new instance can be started up
    # in a new thread.
    # Bot initialization will handle the creation of a new BotInstance.
    if instance.state == STOPPED:
        win = WindowHandler().grab(hwnd=window)
        configuration = Configuration.objects.get(pk=config)
        Thread(target=Bot, kwargs={
            'configuration': configuration,
            'window': win,
            'instance': instance,
            'start': True
        }).start()


def pause(instance):
    """Attempt to pause the current BotInstance if it is currently running."""
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="pause", instance=instance)


def stop(instance):
    """Attempt to stop the current BotInstance if it is currently running."""
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="terminate", instance=instance)


def resume(instance):
    """Attempt to resume the current BotInstance if it is currently running."""
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="resume", instance=instance)


class Window(object):
    """Window can be used to define a single window/process."""
    def __init__(self, hwnd, text, rectangle):
        self.hwnd = hwnd
        self.text = text
        self.x = rectangle[0]
        self.y = rectangle[1]
        self.width = rectangle[2] - self.x
        self.height = rectangle[3] - self.y

        # Additionally, based on the size of the emulator, we want
        # to ensure we can pad the x, y value so the title bar is taken
        # into account when things are clicked or searched for...
        # We expect the emulator size to be 480x800, so we can get
        # the padding from this value.
        self.x_padding = self.width - 480
        self.y_padding = self.height - 800

    def __str__(self):
        return "{text} ({x}, {y}, {w}, {h})".format(
            text=self.text, x=self.x, y=self.y, w=self.width, h=self.height)

    def __repr__(self):
        return "<Window: {window}>".format(window=self)

    def find(self, search):
        """
        Check if the specified search key is present in the windows text.
        """
        if type(search) == str:
            search = [search]

        for s in search:
            if self.text.lower().find(s.lower()) != -1:
                return True

        return False

    def json(self):
        """Convert window instance to a json compliant dictionary."""
        return {
            "hwnd": self.hwnd,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "formatted": str(self)
        }


class WindowNotFoundError(Exception):
    pass


class InvalidHwndValue(Exception):
    pass


class WindowHandler(object):
    """Window handle encapsulates all functionality for handling windows and processes needed."""
    def __init__(self):
        self.windows = dict()

    def _cb(self, hwnd, extra):
        """Callback handler used when current windows are enumerated."""
        if hwnd in self.windows:
            pass

        window = Window(
            hwnd=hwnd,
            text=win32gui.GetWindowText(hwnd),
            rectangle=win32gui.GetWindowRect(hwnd))

        self.windows[hwnd] = window

    def enum(self):
        """Begin enumerating windows and generate windows objects."""
        win32gui.EnumWindows(self._cb, None)

    def grab(self, hwnd):
        self.enum()

        try:
            return self.windows[int(hwnd)]
        except KeyError:
            raise WindowNotFoundError()
        except ValueError:
            raise InvalidHwndValue()

    def filter(self, contains, ignore_hidden=True, ignore_smaller=(480, 800)):
        """
        Filter the currently available windows to ones that contain the specified text.

        Hidden (ie: 0x0 sized windows are ignored by default).
        Smaller: (ie: Windows smaller than the specified amount).
        """
        if type(contains) == str:
            contains = [contains]

        dct = {hwnd: window for hwnd, window in self.windows.items() if window.find(contains)}
        if ignore_hidden:
            dct = {hwnd: window for hwnd, window in dct.items() if window.width != 0 and window.height != 0}
        if ignore_smaller:
            dct = {hwnd: window for hwnd, window in dct.items() if window.width > 480 and window.height > 800}

        return dct


# Import/Export Functionality.
def import_model_kwargs(export_string, compression_keys=None):
    """
    Import a given export string back into the current model that the mixin is present on.
    """
    kwargs = {}
    # Let's begin parsing out the export string provided...
    # Fixup leading/trailing whitespace issues.
    export_string = export_string.lstrip().rstrip()
    export_attrs = export_string.split(ATTR_SEPARATOR)

    for attribute in export_attrs:
        key, value = attribute.split(VALUE_SEPARATOR)

        # Initially, we must check if a compression key was used to shorten the key of this value.
        # If so, we'll convert back to the correct value name.
        if compression_keys:
            for c_key, c_val in compression_keys.items():
                if key == str(c_val):
                    key = c_key
                    break

        # At this point, "key" should be the name of a value available on the model.
        # We now need to parse the value itself...
        # Is a boolean value being used (BOOL SEP + "T" Or "F")/
        if len(value) == 3 and BOOLEAN_PREFIX in value:
            if value[2] == "T":
                value = True
            elif value[2] == "F":
                value = False

            kwargs[key] = value
            continue

        # Is a foreign key value specified?
        if FK_PREFIX in value:
            kwargs[key] = [value.replace(FK_PREFIX, "")]
            if kwargs[key][0] == "None":
                kwargs[key][0] = None
            continue

        # Is a many to many value specified?
        if M2M_PREFIX in value:
            value = value.replace(M2M_PREFIX, "")
            kwargs[key] = [val for val in value.split(M2M_SEPARATOR)]
            for index, v in enumerate(kwargs[key]):
                if v == "None":
                    kwargs[key][index] = None
            continue

        # This case means we reached some sort of char field of plain
        # text input field.
        try:
            kwargs[key] = int(value)
        except ValueError:
            if value == "None":
                kwargs[key] = None
            else:
                kwargs[key] = value

    # We now have the kwargs associated with this exported model.
    return kwargs
