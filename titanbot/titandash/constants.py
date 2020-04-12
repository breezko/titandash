# Generate constants to determine a Bot instance's state.
RUNNING = "running"
PAUSED = "paused"
STOPPED = "stopped"

# Generate constants to determine a Configuration's logging values/choices.
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"

LOGGING_LEVEL_CHOICES = (
    (DEBUG, "Debug"),
    (INFO, "Info"),
    (WARNING, "Warning"),
    (ERROR, "Error"),
    (CRITICAL, "Critical"),
)

SKILL_MAX_LEVEL = 30
SKILL_MAX_CHOICE = "max"
SKILL_DISABLE_CHOICE = "disable"
SKILL_LEVEL_CHOICES = (
    (SKILL_MAX_CHOICE, "Max Level"),
    (SKILL_DISABLE_CHOICE, "Disable"),
)

NO_PERK = "none"
MEGA_BOOST = "mega_boost"
POWER_OF_SWIPING = "power_of_swiping"
ADRENALINE_RUSH = "adrenaline_rush"
MAKE_IT_RAIN = "make_it_rain"
MANA_POTION = "mana_potion"
DOOM = "doom"
CLAN_CRATE = "clan_crate"

PERK_CHOICES = (
    (NO_PERK, "None"),
    (MEGA_BOOST, "Mega Boost"),
    (POWER_OF_SWIPING, "Power Of Swiping"),
    (ADRENALINE_RUSH, "Adrenaline Rush"),
    (MAKE_IT_RAIN, "Make It Rain"),
    (MANA_POTION, "Mana Potion"),
    (DOOM, "Doom"),
    (CLAN_CRATE, "Clan Crate"),
)

for i in range(1, SKILL_MAX_LEVEL + 1):
    SKILL_LEVEL_CHOICES += ((str(i), str(i)),)

# Convert datetimes into human readable strings...
DATETIME_FMT = "%m/%d/%Y %I:%M:%S %p"

# Caching settings.
# Clear cached data after an hour of use...
CACHE_TIMEOUT = 3600

# Import/Export Constants.
GENERIC_BLACKLIST = ["id", "created_at", "updated_at", "deleted_at"]
M2M_SEPARATOR = "|"
ATTR_SEPARATOR = "&"
VALUE_SEPARATOR = ":"
BOOLEAN_PREFIX = "+B"
M2M_PREFIX = "+M"
FK_PREFIX = "+F"
