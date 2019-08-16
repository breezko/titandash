from django.conf import settings as titandash_settings
import settings as bot_settings

import json
import os


def bot(request):
    context = {
        "BOT": {
            "STAGE_CAP": bot_settings.STAGE_CAP,
            "GAME_VERSION": bot_settings.GAME_VERSION,
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


def themes(request):
    context = {
        "THEMES": {
            "selected": None,
            "available": [],
        }
    }

    cookie = request.COOKIES.get("theme")
    if not cookie:
        cookie = "default"

    context["THEMES"]["selected"] = cookie

    # Place default theme as first theme available.
    for file in [f.split(".")[0] for f in os.listdir(bot_settings.THEMES_DIR)]:
        if file == "default":
            context["THEMES"]["available"].append({"theme": file, "selected": cookie and cookie == file})
    # Place other themes after default.
    for file in [f.split(".")[0] for f in os.listdir(bot_settings.THEMES_DIR)]:
        if file != "default":
            context["THEMES"]["available"].append({"theme": file, "selected": cookie and cookie == file})

    return context
