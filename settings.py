"""
settings.py

Store all project specific settings here.
"""
import os
import git

BOT_VERSION = "1.0.0"

# Create an additional directory to place database files into
# so that new versions and releases can rely on the same database.
APP_DATA_DIR = os.getenv("APPDATA")
TITAN_DATA_DIR = os.path.join(APP_DATA_DIR, "titandash")
DATABASE_DIR = os.path.join(TITAN_DATA_DIR, "db")

# Generate directories if they don't exist already...
# Database file will be placed here.
if not os.path.exists(TITAN_DATA_DIR):
    os.makedirs(TITAN_DATA_DIR)

if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

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

# Tool directory.
TOOL_DIR = os.path.join(BOT_DIR, "tools")
# Tool log directory.
TOOL_LOG_DIR = os.path.join(TOOL_DIR, "logs")

# Make sure a "logs" directory actually exists.
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Make sure a "logs" directory exists for bot tools.
if not os.path.exists(TOOL_LOG_DIR):
    os.makedirs(TOOL_LOG_DIR)

# Create a variable that represents the current git commit (sha) of project.
GIT_COMMIT = git.Repo(ROOT_DIR).head.commit.hexsha

# In game specific settings should be stored here. As the game is updated, these will change
# and reflect the new constants that may be used by the bot.
GAME_VERSION = "3.1.1"
STAGE_CAP = 70000
