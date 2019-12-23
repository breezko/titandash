from settings import LOG_DIR

import re
import datetime

# Raid notifications string used to template out the message sent to a user.
RAID_NOTIFICATION_MESSAGE = "Raid attacks are available! You may now attack the active titan!"

# The lookup multiplier is used to convert in game values that are formatted with specific multipliers
# (K, M, T) into their respective float values, or the closest we can get to the actual value. These
# values can then be parsed and diffed.
STATS_LOOKUP_MULTIPLIER = {
    'K': 10**3,
    'M': 10**6,
}

# Regex used to extract the days, hours, minutes and seconds out of the strings used in game to
# determine time deltas.
STATS_DURATION_RE = re.compile(
    r'^((?P<days>[.\d]+?)d) ?((?P<hours>[.\d]+?):)?((?P<minutes>[.\d]+?):)?((?P<seconds>[.\d]+?)?$)'
)

# Format string used when converting time delta objects back into their respective format found in game.
STATS_TIMEDELTA_STR = "{D}d {H}:{M}:{S}"
# Stats date format for session keys.
STATS_DATE_FMT = "%Y-%m-%d"

# Logger name used when grabbing logger.
LOGGER_NAME = "tt2_py"
# Logging format string.
LOGGER_FORMAT = "[%(asctime)s] %(levelname)s [{instance}] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
# Logging file name format string here.
LOGGER_FILE_NAME_STRFMT = "%Y-%m-%d_%H-%M-%S"
INIT_DATE_FMT = datetime.datetime.strftime(datetime.datetime.now(), LOGGER_FILE_NAME_STRFMT)
LOGGER_FILE_NAME = "{log_dir}/{name}.log".format(log_dir=LOG_DIR, name=INIT_DATE_FMT)

# Threshold used to determine if the value of the next parsed stage is obviously malformed.
# This can be determined by looking at the new value, subtracting it from the old value and seeing
# if it crosses the threshold, in which case we can skip the current parse attempt.
STAGE_PARSE_THRESHOLD = 10000

# Determine how many loops are possible before giving up functionality
# (due to an error in game that causes the ui to lag and the bot to miss an image check).
# Now, ideally, no UI errors should come up if the bots functionality is working as intended.
# Although some issues still sneak by as every use case can not be totally locked down. This is a final fallback.
# Also, this value represents the UPPER limit of a failed case. Since some loops may take numerous attempts
# before succeeding (artifact scrolling in particular). So this can be set to a decently large value.
FUNCTION_LOOP_TIMEOUT = 40
# Used for entering/leaving boss fights in game. Can be made a bit smaller
# than the base FUNCTION_LOOP_TIMEOUT since after about 7-10 tries, if we haven't
# succeeded, the bot is likely stuck due to in game damage being too low currently.
# In which case, we can continue and attempt to up this damage and try again later.
BOSS_LOOP_TIMEOUT = int(FUNCTION_LOOP_TIMEOUT / 4)

# Specify the filter strings used to find emulator windows.
NOX_WINDOW_FILTER = [
    "nox", "noxplayer",
]
MEMU_WINDOW_FILTER = [
    "memu"
]
