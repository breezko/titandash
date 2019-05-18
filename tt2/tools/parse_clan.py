"""
parse_clan.py

Make use of this file to manually start a check to parse out all current
statistics from your current clan.
"""
from settings import TOOL_LOG_DIR, CONFIG_FILE
from tt2.core.bot import Bot
from tt2.core.utilities import make_logger

import datetime

LOGGER_FILE_NAME_STRFMT = "%Y-%m-%d_%H-%M-%S"
INIT_DATE_FMT = datetime.datetime.strftime(datetime.datetime.now(), LOGGER_FILE_NAME_STRFMT)
LOGGER_FILE_NAME = "{log_dir}/{file}-{name}.log".format(
    file="parse_clan", log_dir=TOOL_LOG_DIR, name=INIT_DATE_FMT
)
logger = make_logger(log_file=LOGGER_FILE_NAME)


def parse_clan():
    """Begin clan parsing here through a Bot instance."""
    logger.info("beginning clan parsing process")
    logger.info("generating a bot instance to perform screen grabs and parsing")

    bot = Bot(CONFIG_FILE, logger=logger)
    bot.manual_parse_clan_data()
