"""
tester.py

Place any helpful functions or commands that can be used to actively test different parts of a instantiated Bot.
"""

from titandash.models.configuration import Configuration
from titandash.bot.core.bot import Bot


def make_bot():
    """
    Create a Bot with the first available configuration object.

    Note: The bot is never started here, just instantiated, allowing you to call any function
          available on the Bot without looping through the main Bot loops.

    Usage:
    from titandash.bot.core.tester import *; bot = make_bot();
    from titandash.bot.core.tester import *; bot = make_bot(); bot.owned_artifacts = bot.get_upgrade_artifacts(); bot.next_artifact_index = 0; bot.update_next_artifact_upgrade()

    from titandash.bot.core.tester import *; bot = make_bot(); bot.owned_artifacts = bot.get_upgrade_artifacts(); bot.next_artifact_index = 0; bot.update_next_artifact_upgrade(); bot.setup_shortcuts();
    """
    return Bot(configuration=Configuration.objects.first(), start=False)
