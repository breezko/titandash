from django.utils.functional import SimpleLazyObject

from titandash.models.bot import BotInstance
from titandash.models.configuration import ThemeConfig
from titandash.models.globals import GlobalSettings
from titandash.constants import LOGGING_LEVEL_CHOICES

import settings
import json
import os


def bot(request):
    """
    Grab all bot/global settings information that's used by the dashboard lazily.
    """
    def _bot_query():
        """
        Retrieve all information about the bot that is used to derive settings within dashboard.
        """
        dct = {
            "STAGE_CAP": settings.STAGE_CAP,
            "TITANBOT_VERSION": settings.BOT_VERSION,
            "LOG_LEVELS": [level[0] for level in LOGGING_LEVEL_CHOICES]
        }

        # Grab all values from the bot's settings file and generate a key: value for each one.
        values = {k: v for k, v in vars(settings).items() if any(char.isupper() for char in k)}
        for setting, val in {k: v for k, v in values.items() if k not in ["VERSION", "BOT_VERSION", "STAGE_CAP"]}.items():
            dct[setting] = val

        # Including all settings as a json string.
        dct["SETTINGS_JSON"] = json.dumps(dct)

        return dct

    def _globals_query():
        """
        Retrieve all information about global settings used by dashboard.
        """
        return GlobalSettings.objects.grab().json()

    return {
        "BOT": SimpleLazyObject(_bot_query),
        "GLOBALS": SimpleLazyObject(_globals_query)
    }


def instances(request):
    """
    Grab all BotInstances that are currently active and available.
    """
    def _instance_query():
        """
        Use callable to lazily grab information needed.
        """
        lst = []
        for instance in BotInstance.objects.all():
            lst.append(instance.json())
        if len(lst) == 0:
            lst.append(BotInstance.objects.grab().json())

        return lst

    # Returning a simple lazy object that's only called if used by a template.
    # This allows bootstrapping to execute without database errors raised.
    return {
        "INSTANCES": SimpleLazyObject(_instance_query)
    }


def themes(request):
    def _theme_query():
        """
        Use callable to lazily grab information needed.
        """
        dct = {
            "selected": None,
            "available": []
        }
        try:
            theme = ThemeConfig.objects.grab().theme
        except Exception:
            theme = "default"

        dct["selected"] = theme

        files = [f.split(".")[0] for f in os.listdir(settings.THEMES_DIR) if len(f.split(".")) == 3]
        # Place default theme as first theme available.
        for file in files:
            if file == "default":
                dct["available"].append({"theme": file, "selected": theme == file})
        # Place other themes after default.
        for file in files:
            if file != "default":
                dct["available"].append({"theme": file, "selected": theme == file})

        return dct

    # Returning a simple lazy object that's only called if used by a template.
    # This allows bootstrapping to execute without database errors raised.
    return {
        "THEMES": SimpleLazyObject(_theme_query)
    }
