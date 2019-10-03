"""
settings.py

Store all project specific settings here.
"""
import os
import pathlib
import json


# Version file used to determine the current project version.
VERSION_FILE = "version.json"

# Store the root directory of the project. May be used and appended to files in other directories without
# the need for relative urls being generated to travel to the file.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT_DIR, VERSION_FILE), "r") as version_file:
    BOT_VERSION = json.load(version_file)["version"]

# Specify the port that the django server will listen on.
TITANDASH_PORT = 8000

# Specify the url used by the application to derive accessible status.
TITANDASH_DASHBOARD_URL = "http://localhost:%d/" % TITANDASH_PORT
TITANDASH_LOADER_URL = "http://localhost:%d/bootstrap" % TITANDASH_PORT

# Grab the windows local users directory (ie: C:/Users/<username>).
USER_DIR = str(pathlib.Path.home())
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

# Scripts.
PROGRAM_BAT = os.path.join(ROOT_DIR, "titandash.bat")
PROGRAM_SETUP_BAT = os.path.join(ROOT_DIR, "setup.bat")

# Additional data directories used to store local data
# on the users machine.
LOCAL_DATA_DIR = os.path.join(USER_DIR, ".titandash")
# Directory to store our database in.
LOCAL_DATA_DB_DIR = os.path.join(LOCAL_DATA_DIR, "db")
# Directory to store newly downloaded version in.
LOCAL_DATA_UPDATE_DIR = os.path.join(LOCAL_DATA_DIR, "update")
# Directory to store the latest backup in.
LOCAL_DATA_BACKUP_DIR = os.path.join(LOCAL_DATA_DIR, "backup")
# Directory to store our titandash logs in.
LOCAL_DATA_LOG_DIR = os.path.join(LOCAL_DATA_DIR, "logs")

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


def user_directory():
    """
    Perform some idempotent functionality to generate our user directory that contains
    some local data used by titandash. The goal here is to create a location to place files
    that remain even throughout updates to the program.
    """
    if not os.path.exists(LOCAL_DATA_DIR):
        os.makedirs(LOCAL_DATA_DIR)
    if not os.path.exists(LOCAL_DATA_DB_DIR):
        os.makedirs(LOCAL_DATA_DB_DIR)
    if not os.path.exists(LOCAL_DATA_UPDATE_DIR):
        os.makedirs(LOCAL_DATA_UPDATE_DIR)
    if not os.path.exists(LOCAL_DATA_BACKUP_DIR):
        os.makedirs(LOCAL_DATA_BACKUP_DIR)
    if not os.path.exists(LOCAL_DATA_LOG_DIR):
        os.makedirs(LOCAL_DATA_LOG_DIR)

    # Our local data directory is guaranteed to exist now, check for the existence of our actual
    # database within the codebase, and move it if one exists.
    existing = [p for p in pathlib.Path(ROOT_DIR).glob("**/{titan_db}".format(titan_db=TITAN_DB_NAME))]

    # Renaming and moving the database present into the local database directory.
    # If a database is already present, we can ignore this part so no overwrite of
    # the users database takes place.
    if existing:
        existing[0].rename(TITAN_DB_PATH)


user_directory()


# In game specific settings should be stored here. As the game is updated, these will change
# and reflect the new constants that may be used by the bot.
# Note: This reflect what the project is currently setup to support. Newer versions may be
# released and be fine, but this is a good way to derive whether or not features may be missing.
GAME_VERSION = "3.2.4"
STAGE_CAP = 75000
