"""
constant.py

Store any bot specific values here that should not change at any point.
"""
from settings import LOG_DIR
import re
import datetime

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
LOGGER_FORMAT = "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
# Logging file name format string here.
LOGGER_FILE_NAME_STRFMT = "%Y-%m-%d_%H-%M-%S"
INIT_DATE_FMT = datetime.datetime.strftime(datetime.datetime.now(), LOGGER_FILE_NAME_STRFMT)
LOGGER_FILE_NAME = "{log_dir}/{name}.log".format(log_dir=LOG_DIR, name=INIT_DATE_FMT)

# imagesearch.py will make use of these constants to determine which button to press.
LEFT_CLICK = "left"
RIGHT_CLICK = "right"
MIDDLE_CLICK = "middle"

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
BOSS_LOOP_TIMEOUT = int(FUNCTION_LOOP_TIMEOUT / 2)

# Specify any functions that may be forced.
FORCEABLE_FUNCTIONS = ["recover", "actions", "update_stats", "prestige", "daily_achievement_check", "activate_skills"]

# Specify functions that can be activated through keyboard shortcuts.
# The key present should represent a function that's present on the Bot.
# The value should be the name of a key (or keys with a + used as a delimiter).
SHORTCUT_FUNCTIONS = {
    # Utility shortcuts.
    "pause": "p",
    "resume": "r",
    "terminate": "esc",
    "soft_terminate": "shift+esc",
    # Functional shortcuts.s
    "actions": "shift+a",
    "level_heroes": "shift+h",
    "level_master": "shift+m",
    "level_skills": "shift+s",
    "artifacts": "shift+a",
    "daily_rewards": "shift+d",
    "hatch_eggs": "shift+h",
    "fight_boss": "shift+f",
    "leave_boss": "shift+l",
    "update_stats": "shift+u",
    "prestige": "shift+p",
    "daily_achievement_check": "ctrl+d",
    "activate_skills": "ctrl+a",
}

# Reverse the original SHORTCUT_FUNCTIONS dictionary, so we can access functions by their shortcut value.
FUNCTION_SHORTCUTS = {v: k for k, v in SHORTCUT_FUNCTIONS.items()}

# Specify any functions that be queued. These will be grabbed by the TitanDashboard to provide a user
# with the ability to manually add functions that will be executed by the Bot.
QUEUEABLE_FUNCTIONS = FORCEABLE_FUNCTIONS + [
    "calculate_next_action_run", "calculate_next_stats_update", "calculate_next_daily_achievement_check",
    "calculate_next_skill_execution", "calculate_next_prestige", "calculate_next_recovery_reset", "update_next_artifact_upgrade",
    "parse_current_stage", "level_heroes", "level_master", "level_skills", "artifacts", "parse_artifacts", "check_tournament",
    "daily_rewards", "hatch_eggs", "clan_crate", "collect_ad", "fight_boss", "leave_boss", "tap",
    "pause", "resume", "terminate", "soft_terminate"
]

# Also generating a dictionary of tooltips or help texts associated with each queueable function.
QUEUEABLE_TOOLTIPS = {
    "calculate_next_action_run": "Calculate the next time that an action run will take place.",
    "calculate_next_stats_update": "Calculate the next time a statistics update will take place.",
    "calculate_next_daily_achievement_check": "Calculate the next time a daily achievement check will take place",
    "calculate_next_skill_execution": "Calculate the next time a skill execution will take place.",
    "calculate_next_prestige": "Calculate the next time a prestige will take place.",
    "calculate_next_recovery_reset": "Calculate the next time a recovery reset will tak place.",
    "update_next_artifact_upgrade": "Update the next artifact that will be upgraded.",
    "parse_current_stage": "Parse the current stage in game.",
    "level_heroes": "Level heroes in game.",
    "level_master": "Level sword master in game.",
    "level_skills": "Level skills in game.",
    "artifacts": "Upgrade the specified next artifact upgrade in game.",
    "parse_artifacts": "Begin a parse of all owned artifacts in game.",
    "check_tournament": "Check for a tournament and join/prestige if one is available.",
    "daily_rewards": "Check for daily rewards in game and collect if available.",
    "hatch_eggs": "Check for eggs in game and hatch them if available.",
    "clan_crate": "Check for a clan crate in game and collect if available.",
    "collect_ad": "Collect an ad in game if one is available.",
    "fight_boss": "Attempt to begin the boss fight in game.",
    "leave_boss": "Attempt to leave the boss fight in game.",
    "tap": "Begin tapping process in game.",
    "pause": "Pause all bot functionality.",
    "resume": "Resume all bot functionality.",
    "terminate": "Terminate all bot functionality.",
    "soft_terminate": "Perform a soft termination of all bot functionality.",
    "recover": "Force a recovery in game.",
    "actions": "Force all actions to be executed in game.",
    "update_stats": "Force a statistics update in game.",
    "prestige": "Force a prestige in game.",
    "daily_achievement_check": "Force a daily achievement check in game.",
    "activate_skills": "Force a skill activation in game."
}

PROPERTIES = [
    "current_stage", "current_function", "next_action_run", "next_prestige",
    "next_stats_update", "next_recovery_reset", "next_daily_achievement_check",
    "next_clan_results_parse", "next_heavenly_strike", "next_deadly_strike",
    "next_hand_of_midas", "next_fire_sword", "next_war_cry", "next_shadow_clone"
]
