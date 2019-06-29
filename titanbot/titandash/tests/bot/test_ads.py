"""
test_ads.py

Test functionality related to the image search functionality when
used to search for and collect ads in game.
"""
from titandash.tests.bot.base import BaseBotTest


class TestBotAdPrompts(BaseBotTest):
    """Test functionality related to in game ad image recognition."""
    def test_collect_on_screen(self):
        """Test that the bot can determine if the collect icon is present."""
        self.is_image_visible(
            game_image=self.TEST_IMAGES["ADS"]["skill_prompt"],
            find_image=self.BOT_IMAGES["ADS"]["collect_ad"])

    def test_no_thanks_on_screen(self):
        """Test that the bot can determine if the no thanks icon is present."""
        self.is_image_visible(
            game_image=self.TEST_IMAGES["ADS"]["skill_prompt"],
            find_image=self.BOT_IMAGES["ADS"]["no_thanks"])
