"""
test_props.py

Test functionality related to the Props object used by Bot and BotInstance instances.
"""
from django.test import TestCase

from titandash.models.bot import BotInstance
from titandash.bot.core.constants import PROPERTIES


class TestBotProps(TestCase):
    """Test functionality related to props object here."""
    def test_properties_valid_on_instance(self):
        """Ensure that the BotInstance attributes contain all PROPERTIES."""
        attrs = [att.name for att in BotInstance._meta.fields if not att.name.startswith("_")]
        for prop in PROPERTIES:
            self.assertTrue(prop in attrs)
