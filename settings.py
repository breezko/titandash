"""
settings.py

Store all project specific settings here.
"""
import os
import logging
import pathlib
import textwrap

logger = logging.getLogger(__name__)


BOT_VERSION = "1.5.4.01"


# Grab the windows local users directory (ie: C:/Users/<username>).
USER_DIR = str(pathlib.Path.home())
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

# Additional data directories used to store local data
# on the users machine.
LOCAL_DATA_DIR = os.path.join(USER_DIR, ".titandash")
# Directory to store our database in.
LOCAL_DATA_DB_DIR = os.path.join(LOCAL_DATA_DIR, "db")

# Testing directory.
TEST_DIR = os.path.join(TITANDASH_DIR, "tests")
TEST_BOT_DIR = os.path.join(TEST_DIR, "bot")
TEST_IMAGE_DIR = os.path.join(TEST_BOT_DIR, "images")

# Themes CSS directory.
THEMES_DIR = os.path.join(TITANDASH_DIR, "static/css/theme")

# Make sure a "logs" directory actually exists.
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


TITAN_DB_NAME = "titan.sqlite3"
TITAN_DB_PATH = os.path.join(LOCAL_DATA_DB_DIR, TITAN_DB_NAME)


def git_info():
    """
    Attempt to grab the git information so we can use a proper git commit.

    If git is not present or no repository is being used, we can fallback onto
    not using a git commit anywhere instead.
    """
    try:
        import git
        try:
            return git.Repo(ROOT_DIR).head.commit.hexsha
        except git.InvalidGitRepositoryError:
            return None
    except ImportError:
        return None


GIT_COMMIT = git_info()

# In game specific settings should be stored here. As the game is updated, these will change
# and reflect the new constants that may be used by the bot.
# Note: This reflect what the project is currently setup to support. Newer versions may be
# released and be fine, but this is a good way to derive whether or not features may be missing.
GAME_VERSION = "3.2.4"
STAGE_CAP = 75000
