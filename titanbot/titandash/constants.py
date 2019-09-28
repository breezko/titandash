from django.conf import settings
import pytz


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

# Emulator choices used by Configuration's.
EMULATOR_CHOICES = (
    ("nox", "Nox Emulator"),
)

# Convert datetimes into human readable strings...
DATETIME_FMT = "%m/%d/%Y %I:%M:%S %p"

# Caching settings.
# Clear cached data after an hour of use...
CACHE_TIMEOUT = 3600
