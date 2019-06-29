"""
test_heroes.py

Test functionality related to image search functionality when
used to search for different images on the heroes panel.
"""
from titandash.tests.bot.base import BaseBotTest


class TestHeroesPanels(BaseBotTest):
    """Test functionality related to heroes panel here."""
    @classmethod
    def setUpClass(cls):
        super(TestHeroesPanels, cls).setUpClass()

        # Generate a list of images used when checking visibility.
        # Ensuring that expanded/collapsed panels can find image in question.
        cls.IMAGES = [
            cls.TEST_IMAGES["PANELS"]["heroes_collapsed"],
            cls.TEST_IMAGES["PANELS"]["heroes_expanded"]
        ]

    def test_masteries_on_screen(self):
        """Test that the bot can determine if the masteries icon is on the screen."""
        for image in self.IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["HEROES"]["masteries"])

    def test_stats_on_screen(self):
        """Test that the bot can determine if the stats icon is on the screen."""
        for image in self.IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["HEROES"]["stats"])

    def test_story_on_screen(self):
        """Test that the bot can determine if the story icon is on the screen."""
        for image in self.IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["HEROES"]["story"])
