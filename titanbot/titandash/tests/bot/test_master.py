"""
test_master.py

Test functionality related to the image search within any features within the master panel.
"""
from titandash.tests.bot.base import BaseBotTest


class TestMasterPanels(BaseBotTest):
    """Test functionality related to master panel here."""
    @classmethod
    def setUpClass(cls):
        super(TestMasterPanels, cls).setUpClass()

        # Generating list of images used when checking base visibility.
        cls.TOP_IMAGES = [
            cls.TEST_IMAGES["MASTER"]["master_collapsed"],
            cls.TEST_IMAGES["MASTER"]["master_expanded"]]
        cls.BOTTOM_IMAGES = [
            cls.TEST_IMAGES["MASTER"]["master_bottom_expanded"],
            cls.TEST_IMAGES["MASTER"]["master_bottom_collapsed"]]

    def test_raid_cards_on_screen(self):
        """Test that the bot can determine if the raid cards icon is on the screen."""
        for image in self.TOP_IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["MASTER"]["raid_cards"])

    def test_skill_tree_on_screen(self):
        """Test that the bot can determine if the skill tree icon is on the screen."""
        for image in self.TOP_IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["MASTER"]["skill_tree"])

    def test_achievements_on_screen(self):
        """Test that the bot can determine if the achievements icon is on the screen."""
        for image in self.TOP_IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["MASTER"]["achievements"])

    def test_inbox_on_screen(self):
        """Test that the bot can determine if the inbox icon is on the screen."""
        for image in self.TOP_IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["MASTER"]["inbox"])

    def test_master_on_screen(self):
        """Test that the bot can determine if the master icon is on the screen."""
        for image in self.TOP_IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["MASTER"]["master"])

    def test_skills_on_screen(self):
        """Test that the bot can determine if the skills are all on the screen."""
        for image in [
            self.BOT_IMAGES["MASTER"]["heavenly_strike"],
            self.BOT_IMAGES["MASTER"]["deadly_strike"],
            self.BOT_IMAGES["MASTER"]["hand_of_midas"],
            self.BOT_IMAGES["MASTER"]["fire_sword"],
            self.BOT_IMAGES["MASTER"]["war_cry"],
            self.BOT_IMAGES["MASTER"]["shadow_clone"]
        ]:
            self.is_image_visible(
                game_image=self.TEST_IMAGES["MASTER"]["master_expanded"],
                find_image=image)

    def test_prestige_on_screen(self):
        """Test that the bot can determine if the prestige icon is on the screen."""
        for image in self.BOTTOM_IMAGES:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["MASTER"]["prestige"])

    def test_prestige_confirm_on_screen(self):
        """Test that the bot can determine if the prestige confirmation is on the screen."""
        self.is_image_visible(
            game_image=self.TEST_IMAGES["MASTER"]["master_prestige_open"],
            find_image=self.BOT_IMAGES["MASTER"]["confirm_prestige"])
