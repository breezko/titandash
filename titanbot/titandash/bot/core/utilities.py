"""
utilities.py

Any utility or backing functions can be placed here and imported when needed.
"""
from settings import LOG_DIR
from titandash.bot.external.imagesearch import *
from .maps import MASTER_LOCS
from .constants import (
    STATS_DURATION_RE, STATS_LOOKUP_MULTIPLIER, STATS_TIMEDELTA_STR,
    LOGGER_NAME, LOGGER_FORMAT, LOGGER_FILE_NAME, LOGGER_FILE_NAME_STRFMT,
    RAID_NOTIFICATION_MESSAGE
)

from channels.generic.websocket import async_to_sync
from channels.layers import get_channel_layer

from twilio.rest import Client

from string import Template, Formatter
from pyautogui import *

import datetime
import logging
import time
import math

logger = logging.getLogger(LOGGER_NAME)


def sleep(seconds):
    """
    Wrap the time.sleep method to allow for logging the time to sleep for.
    """
    logger.debug("sleeping for {seconds} second(s)".format(seconds=seconds))
    time.sleep(seconds)


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(timedelta, fmt=STATS_TIMEDELTA_STR):
    """
    Format a timedelta object in the given format.
    """
    f = Formatter()
    d = {}
    lst = {"D": 86400, "H": 3600, "M": 60, "S": 1}
    k = map(lambda x: x[1], list(f.parse(fmt)))
    remainder = int(timedelta.total_seconds())

    for i in ("D", "H", "M", "S"):
        if i in k and i in lst.keys():
            d[i], remainder = divmod(remainder, lst[i])

    for key, value in d.items():
        if value < 10 and "D" not in key:
            d[key] = "0" + str(value)
    return f.format(fmt, **d)


def strfnumber(number):
    """
    Return a number with properly formatted thousand separators.

    ie: 43123 -> "43,123"
    """
    if number:
        return "{:,}".format(int(number))
    else:
        return None


def convert(value):
    """
    Attempt to convert a given value into its appropriate integer value.
    """
    try:
        return float(value)
    except ValueError:
        pass
    except TypeError:
        return value

    unit = value[-1]
    try:
        number = float(value[:-1])
    except ValueError:
        number = None

    if not number:
        return value

    if unit in STATS_LOOKUP_MULTIPLIER:
        return STATS_LOOKUP_MULTIPLIER[unit] * number
    return number


def diff(old, new):
    """
    Determine the difference between values. The accepted values here may be
    datetime objects, floats, or integers.
    """
    if isinstance(old, (int, float)) and isinstance(new, (int, float)):
        value = new - old

        # Infinity/NAN values should be dealt with by just returning a readable string.
        # Users can manually audit the changes since they're exponential.
        if math.isnan(value) or math.isinf(value):
            return "TOO BIG"

        try:
            return int(value)
        except ValueError:
            return value

    # Maybe a date is being diffed?
    if isinstance(old, str) and isinstance(new, str):
        try:
            old_params = {
                name: float(param) for name, param in STATS_DURATION_RE.match(old).groupdict().items() if param
            }
            new_params = {
                name: float(param) for name, param in STATS_DURATION_RE.match(new).groupdict().items() if param
            }

            old_td = datetime.timedelta(**old_params)
            new_td = datetime.timedelta(**new_params)

            delta = new_td - old_td
            return strfdelta(delta)

        # Gracefully exit and return None, treated as null in JSON.
        except Exception as exc:
            logger.error("error occurred while getting diff between {old}, {new} - {exc}".format(
                old=old, new=new, exc=exc))
            return "ERROR DIFFING"
    return None


def delta_from_values(values):
    """
    Generate a delta from the given values. The values expected here should contain the number and
    letter associated with the value being parsed (ie: ["1d", "4h", "32m"])
    """
    kwargs = {"days": 0, "hours": 0, "minutes": 0}

    try:
        for value in values:
            # DAYS.
            if value.endswith("d"):
                kwargs["days"] = int(value[:-1])

            # HOURS.
            if value.endswith("h"):
                kwargs["hours"] = int(value[:-1])

            # MINUTES.
            if value.endswith("m"):
                kwargs["minutes"] = int(value[:-1])

    except ValueError:
        return None

    delta = datetime.timedelta(**kwargs)
    if delta.total_seconds() == 0:
        return None

    return datetime.timedelta(**kwargs)


def send_raid_notification(sid, token, from_num, to_num):
    """
    Using the Twilio Rest Client, send a sms message to the specified phone number.
    """
    return Client(sid, token).messages.create(
        to=to_num,
        from_=from_num,
        body=RAID_NOTIFICATION_MESSAGE
    )


def gen_offset(point, amount):
    """
    Add some offset to a given point.
    """
    if amount == 0:
        return point

    rand_x = random.randint(-amount, amount)
    rand_y = random.randint(-amount, amount)
    return point[0] + rand_x, point[1] + rand_y


def click_on_point(point, window, clicks=1, interval=0.0, button="left", pause=0.0, offset=5, disable_padding=False):
    """
    Click on the specified X, Y value based on the point passed along as a parameter.
    """
    if not disable_padding:
        padded = window.y + window.y_padding
        point = (point[0] + window.x, point[1] + padded)

    if offset != 0:
        point = gen_offset(point, offset)

    logger.debug("{button} clicking {point} on screen {clicks} time(s) with {interval} interval and {pause} pause".format(button=button, point=point, clicks=clicks, interval=interval, pause=pause))
    click((point[0], point[1]), clicks=clicks, interval=interval, button=button, pause=pause)


def move_to_point(point, window, pause=0.0):
    """
    Move the mouse to the specified X, Y values based on the point passed along as a parameter.
    """
    padded = window.y + window.y_padding
    point = (point[0] + window.x, point[1] + padded)

    moveTo(point[0], point[1], pause=pause)


def click_on_image(image=None, pos=None, button="left", pause=0.0):
    """
    Click on the specified image on the screen.
    """
    logger.debug("{button} clicking on {image} located at {pos} with {pause}s pause".format(button=button, image=image, pos=pos, pause=pause))
    click_image(image=image, pos=pos, action=button, timestamp=0, pause=pause)


def drag_mouse(start, end, window, button="left", duration=0.3, pause=0.5, tween=linear, quick_stop=None):
    """
    Drag the mouse from the starting position, to the end position.
    """
    logger.debug("{button} clicking and dragging mouse from {start} to {end} over {duration}s with quick stop {quick}".format(button=button, start=start, end=end, duration=duration, quick="enabled" if quick_stop else "disabled"))

    padded = window.y + window.y_padding
    start = (start[0] + window.x, start[1] + padded)
    end = (end[0] + window.x, end[1] + padded)
    moveTo(start[0], start[1])

    # Determine pause amount tween. Tweening may be useful for specific actions
    # since dragging may continue after drag is finished.
    pause = pause if not quick_stop else 0

    dragTo(end[0], end[1], duration=duration, button=button, pause=pause, tween=tween)

    if quick_stop:
        click_on_point((quick_stop[0], quick_stop[1]), window=window, pause=0.5, offset=0)


def in_transition_func(*args, max_loops):
    """
    Directly call this function to perform the transition state check.
    """
    _self = args[0]
    loops = 0
    while True:
        # Is a panel open that should be closed? This large exit panel will close any in game
        # panels that may of been opened on accident.
        found, pos = _self.grabber.search(_self.images.large_exit_panel)
        if found:
            click_on_image(image=_self.images.large_exit_panel, pos=pos, pause=0.5)

        # Is an ad panel open that should be accepted/declined?
        _self.collect_ad_no_transition()

        # At least one of these three generic images should be on the screen
        # if the game is not in a transition state.
        if _self.grabber.search(_self.images.exit_panel, bool_only=True):
            break
        if _self.grabber.search(_self.images.clan_no_raid, bool_only=True):
            break
        if _self.grabber.search(_self.images.clan_raid_ready, bool_only=True):
            break

        # Can a stage be parsed out in the game?
        if not _self.stats.stage_ocr() == '':
            break

        # Clicking the top of the screen in case of a transition taking place due to something being
        # present on the screen that requires clicking.
        _self.click(point=MASTER_LOCS["screen_top"], clicks=3, pause=0.5)
        _self.logger.info("in a transition? waiting one second before continuing")
        sleep(1)

        loops += 1
        if loops == max_loops:
            # In this case, the game may of broke? A crash may of occurred. It's safe to attempt to restart the
            # game at this point.
            _self.logger.error("unable to resolve transition state of game, attempting to restart game.")
            _self.recover(force=True)


class TitanBotHandler(logging.StreamHandler):
    def __init__(self, instance, stream=None):
        super(TitanBotHandler, self).__init__()
        self.instance = instance
        self.channel_layer = get_channel_layer()
        self.group_name = 'titan_log'

    def format_record(self, record):
        return "[{asctime}] {levelname} [{instance}] [{filename} - {funcName} ] {message}".format(
            asctime=record.asctime, levelname=record.levelname, instance=self.instance.name, filename=record.filename, funcName=record.funcName, message=record.message
        )

    def emit(self, record):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {
                'type': 'emitted',
                'instance_id': self.instance.pk,
                'record': {
                    "message": self.format_record(record)
                }
            }
        )


def generate_log_file_name(instance):
    """
    Generate a log file name with the current date.
    """
    init_date_fmt = datetime.datetime.strftime(datetime.datetime.now(), LOGGER_FILE_NAME_STRFMT)
    init_date_fmt = instance.name.replace(" ", "_").lower() + "_" + init_date_fmt
    return "{log_dir}/{name}.log".format(log_dir=LOG_DIR, name=init_date_fmt)


def make_logger(instance, log_level="INFO", log_format=LOGGER_FORMAT, log_name=LOGGER_NAME, log_file=LOGGER_FILE_NAME):
    """
    Grab the logging instance that will be used throughout bot runtime.
    """
    log_formatter = logging.Formatter(log_format.format(instance=instance.name))
    _logger = logging.getLogger("{log_name}.{instance}".format(log_name=log_name, instance=instance.pk))

    if not len(logger.handlers):
        if not log_file:
            log_file = generate_log_file_name(instance=instance)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(log_formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        socket_handler = TitanBotHandler(instance=instance)
        socket_handler.setFormatter(log_formatter)

        _logger.addHandler(file_handler)
        _logger.addHandler(console_handler)
        _logger.addHandler(socket_handler)

    _logger.setLevel(log_level)
    return _logger
