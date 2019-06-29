"""
test_panels.py

Test functionality related to generic panel search functionality.
"""
from titandash.tests.bot.base import BaseBotTest


class TestPanels(BaseBotTest):
    """Test functionality related to in-game panels here."""
    def test_any_panels_on_screen(self):
        """Test that the bot can determine if any panels are currently open or not."""
        # Generating a list of images that should contain the "exit_panel" image.
        present = [
            self.TEST_IMAGES["PANELS"]["artifacts_collapsed"],
            self.TEST_IMAGES["PANELS"]["artifacts_expanded"],
            self.TEST_IMAGES["PANELS"]["equipment_collapsed"],
            self.TEST_IMAGES["PANELS"]["equipment_expanded"],
            self.TEST_IMAGES["PANELS"]["heroes_collapsed"],
            self.TEST_IMAGES["PANELS"]["heroes_expanded"],
            self.TEST_IMAGES["PANELS"]["master_collapsed"],
            self.TEST_IMAGES["PANELS"]["master_expanded"],
            self.TEST_IMAGES["PANELS"]["pets_collapsed"],
            self.TEST_IMAGES["PANELS"]["pets_expanded"],
            self.TEST_IMAGES["PANELS"]["shop_open"]]
        # Generating a list of images that should not contain the "exit_panel" image.
        not_present = [
            self.TEST_IMAGES["PANELS"]["no_panel_open"]]

        for image in present:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["GENERIC"]["exit_panel"])

        for image in not_present:
            self.is_image_not_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["GENERIC"]["exit_panel"])

    def test_panel_collapse_on_screen(self):
        """Test that the bot can determine if the collapse button is present on the screen."""
        # Generating a list of images that should contain the "collapse_panel" image.
        present = [
            self.TEST_IMAGES["PANELS"]["artifacts_expanded"],
            self.TEST_IMAGES["PANELS"]["equipment_expanded"],
            self.TEST_IMAGES["PANELS"]["heroes_expanded"],
            self.TEST_IMAGES["PANELS"]["master_expanded"],
            self.TEST_IMAGES["PANELS"]["pets_expanded"]]
        # Generating a list of images that should not contain the "collapse_panel" image.
        not_present = [
            self.TEST_IMAGES["PANELS"]["artifacts_collapsed"],
            self.TEST_IMAGES["PANELS"]["equipment_collapsed"],
            self.TEST_IMAGES["PANELS"]["heroes_collapsed"],
            self.TEST_IMAGES["PANELS"]["master_collapsed"],
            self.TEST_IMAGES["PANELS"]["no_panel_open"],
            self.TEST_IMAGES["PANELS"]["shop_open"]]

        for image in present:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["GENERIC"]["collapse_panel"])

        for image in not_present:
            self.is_image_not_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["GENERIC"]["collapse_panel"])

    def test_panel_expand_on_screen(self):
        """Test that the bot can determine if the expand button is present on the screen."""
        # Generating a list of images that should contain the "expand_panel" image.
        present = [
            self.TEST_IMAGES["PANELS"]["artifacts_collapsed"],
            self.TEST_IMAGES["PANELS"]["equipment_collapsed"],
            self.TEST_IMAGES["PANELS"]["heroes_collapsed"],
            self.TEST_IMAGES["PANELS"]["master_collapsed"]]
        # Generating a list of images that should not contain the "expand_panel" image.
        not_present = [
            self.TEST_IMAGES["PANELS"]["artifacts_expanded"],
            self.TEST_IMAGES["PANELS"]["equipment_expanded"],
            self.TEST_IMAGES["PANELS"]["heroes_expanded"],
            self.TEST_IMAGES["PANELS"]["master_expanded"],
            self.TEST_IMAGES["PANELS"]["pets_expanded"],
            self.TEST_IMAGES["PANELS"]["no_panel_open"],
            self.TEST_IMAGES["PANELS"]["shop_open"]]

        for image in present:
            self.is_image_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["GENERIC"]["expand_panel"])

        for image in not_present:
            self.is_image_not_visible(
                game_image=image,
                find_image=self.BOT_IMAGES["GENERIC"]["expand_panel"])

    def test_panel_buy_options(self):
        """Test that the bot can determine if the different buy options are present on the screen."""
        # Generating a list of images where buy options should be present in each.
        images = [
            self.TEST_IMAGES["PANELS"]["master_buy_option_open_collapsed"],
            self.TEST_IMAGES["PANELS"]["master_buy_option_open_expanded"]
        ]
        # Generating a list of images for each buy options present.
        options = [
            self.BOT_IMAGES["GENERIC"]["buy_max"],
            self.BOT_IMAGES["GENERIC"]["buy_one"],
            self.BOT_IMAGES["GENERIC"]["buy_ten"],
            self.BOT_IMAGES["GENERIC"]["buy_one_hundred"],
            self.BOT_IMAGES["GENERIC"]["max"],
        ]

        for image in images:
            for option in options:
                self.is_image_visible(
                    game_image=image,
                    find_image=option)
