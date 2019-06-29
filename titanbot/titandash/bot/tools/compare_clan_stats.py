"""
parse_clan.py

Make use of this file to manually start a comparison between the specified clan statistic parsed stats.
"""
from settings import TOOL_LOG_DIR, CONFIG_FILE
from titanbot.bot.core.bot import Bot
from titanbot.bot.core.utilities import make_logger

import datetime

LOGGER_FILE_NAME_STRFMT = "%Y-%m-%d_%H-%M-%S"
INIT_DATE_FMT = datetime.datetime.strftime(datetime.datetime.now(), LOGGER_FILE_NAME_STRFMT)
LOGGER_FILE_NAME = "{log_dir}/{file}-{name}.log".format(
    file="parse_artifacts", log_dir=TOOL_LOG_DIR, name=INIT_DATE_FMT
)
logger = make_logger(log_file=LOGGER_FILE_NAME)


def compare_clan_stats(code, keys):
    """Begin comparison between both keys specified for the given clan."""
    logger.info("beginning clan statistics comparison process")
    logger.info("generating a bot instance to perform clan comparisons.")

    bot = Bot(CONFIG_FILE, logger=logger)

    bot.stats.compare_clan_stats(code=code, keys=keys)
