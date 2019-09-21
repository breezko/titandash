"""
settings.py

Store all project specific settings here.
"""
import os
import logging

logger = logging.getLogger(__name__)


BOT_VERSION = "1.5.2"
TITAN_DB = "titan.sqlite3"

# Store the root directory of the project. May be used and appended to files in other directories without
# the need for relative urls being generated to travel to the file.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Django project directory (titanbot).
PROJECT_DIR = os.path.join(ROOT_DIR, "titanbot")
# TitanDash project directory (titandash).
TITANDASH_DIR = os.path.join(PROJECT_DIR, "titandash")
# Bot directory (tt2).
BOT_DIR = os.path.join(TITANDASH_DIR, "bot")
# Core bot file directory.
CORE_DIR = os.path.join(BOT_DIR, "core")
# External library file directory.
EXT_DIR = os.path.join(BOT_DIR, "external")
# Log files should be placed here.
LOG_DIR = os.path.join(BOT_DIR, "logs")
# Any data files used directly by the bot should be placed in here.
DATA_DIR = os.path.join(BOT_DIR, "data")
# Additional data directories.
IMAGE_DIR = os.path.join(DATA_DIR, "images")

# Testing directory.
TEST_DIR = os.path.join(TITANDASH_DIR, "tests")
TEST_BOT_DIR = os.path.join(TEST_DIR, "bot")
TEST_IMAGE_DIR = os.path.join(TEST_BOT_DIR, "images")

# Themes CSS directory.
THEMES_DIR = os.path.join(TITANDASH_DIR, "static/css/theme")

# Make sure a "logs" directory actually exists.
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

try:
    import git
except Exception as exc:
    logger.error(exc, exc_info=True)
    pass

# Create a variable that represents the current git commit (sha) of project.
try:
    GIT_COMMIT = git.Repo(ROOT_DIR).head.commit.hexsha
except Exception as exc:
    logger.error(exc, exc_info=True)
    GIT_COMMIT = None

# In game specific settings should be stored here. As the game is updated, these will change
# and reflect the new constants that may be used by the bot.
# Note: This reflect what the project is currently setup to support. Newer versions may be
# released and be fine, but this is a good way to derive whether or not features may be missing.
GAME_VERSION = "3.2.4"
STAGE_CAP = 75000
