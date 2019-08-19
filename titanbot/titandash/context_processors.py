from titandash.models.configuration import ThemeConfig

import settings
import json
import os


def bot(request):
    context = {
        "BOT": {
            "STAGE_CAP": settings.STAGE_CAP,
            "GAME_VERSION": settings.GAME_VERSION,
            "TITANBOT_VERSION": settings.BOT_VERSION
        },
    }

    # Grab all values from the bot's settings file and generate a key: value for each one.
    values = {k: v for k, v in vars(settings).items() if any(char.isupper() for char in k)}
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

    theme = ThemeConfig.objects.grab().theme
    context["THEMES"]["selected"] = theme

    files = [f.split(".")[0] for f in os.listdir(settings.THEMES_DIR) if len(f.split(".")) == 3]
    # Place default theme as first theme available.
    for file in files:
        if file == "default":
            context["THEMES"]["available"].append({"theme": file, "selected": theme == file})
    # Place other themes after default.
    for file in files:
        if file != "default":
            context["THEMES"]["available"].append({"theme": file, "selected": theme == file})

    return context
