from django.conf import settings as titandash_settings
import settings as bot_settings

import json


def bot(request):
    context = {
        "BOT": {
            "STAGE_CAP": bot_settings.STAGE_CAP,
            "GAME_VERSION": bot_settings.GAME_VERSION,
            "TITANDASH_VERSION": titandash_settings.VERSION,
            "TITANBOT_VERSION": bot_settings.BOT_VERSION
        },
    }

    # Grab all values from the bot's settings file and generate a key: value for each one.
    values = {k: v for k, v in vars(bot_settings).items() if any(char.isupper() for char in k)}
    for setting, val in {k: v for k, v in values.items() if k not in ["VERSION", "BOT_VERSION", "GAME_VERSION", "STAGE_CAP"]}.items():
        context["BOT"][setting] = val

    # Including all settings as a json string.
    context["SETTINGS_JSON"] = json.dumps(context["BOT"])

    return context
