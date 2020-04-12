from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings

from titanauth.models.user_reference import ExternalAuthReference

from titandash.bot.core.window import WindowHandler
from titandash.models.bot import BotInstance
from titandash.models.globals import GlobalSettings
from titandash.models.statistics import Session, ArtifactStatistics, Statistics
from titandash.models.configuration import Configuration

from shutil import copy

import settings as bot_settings
import pytesseract
import os
import json
import subprocess
import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class Command(BaseCommand):
    """
    Custom management command used to generate the latest information inside of a users
    titandash directory that may be used to aid in debugging issues.
    """
    help = "Generate error/debugging report in users .titandash directory."

    def handle(self, *args, **kwargs):
        """
        Generate all data and ensure it's been placed into the users directory.
        """
        data = {
            "LAST_SESSION": None,
            "AUTHENTICATION": None,
            "BOT_SETTINGS": {},
            "GLOBAL_SETTINGS": {},
            "DJANGO_SETTINGS": {},
            "ARTIFACTS": {},
            "STATISTICS": {},
            "CONFIGURATIONS": {},
            "MISCELLANEOUS": {},
        }

        # Gather the users current dashboard settings and place
        # all of them into their own dictionary.
        data["BOT_SETTINGS"].update({
            k: v for k, v in vars(bot_settings).items() if any(char.isupper() for char in k)
        })

        # Gather the global settings present and include them in our data.
        data["GLOBAL_SETTINGS"] = GlobalSettings.objects.grab().json()

        # Gather the users current django settings (these should not be modified).
        # But good to have them for debugging.
        data["DJANGO_SETTINGS"].update({
            k: v for k, v in vars(settings).items() if k not in data["BOT_SETTINGS"] and any(char.isupper() for char in k)
        })

        # Retrieve the users last session (if one exists), and place that json representation
        # into our dictionary as well.
        session = Session.objects.all().order_by("-start")
        if session.count() > 0:
            data["LAST_SESSION"] = session.first().json()

        # Including some miscellaneous information that can be added to
        # and used to include some useful variables.
        try:
            data["MISCELLANEOUS"].update({
                "tesseract": {
                    "path": settings.TESSERACT_COMMAND,
                    "version": pytesseract.get_tesseract_version().vstring,
                }
            })
        except Exception:
            pass

        # We also include some generic data from the users information as well.
        # Each instance available may contain different pieces fo information.
        # --------------------------------------------------------------------
        for instance in BotInstance.objects.all():
            # ARTIFACTS.
            data["ARTIFACTS"][instance.name] = ArtifactStatistics.objects.grab(instance=instance).json()
            # STATISTICS.
            data["STATISTICS"][instance.name] = Statistics.objects.grab(instance=instance).json()

        for configuration in Configuration.objects.all():
            data["CONFIGURATIONS"][configuration.name] = configuration.json(condense=True, hide_sensitive=True)

        auth = ExternalAuthReference.objects.all()
        if auth.count() > 0:
            data["AUTHENTICATION"] = auth.first().json(hide_sensitive=True)

        # Purging the debug directory before creating new files.
        # This is done so that multiple logs aren't retained that are not needed.
        for f in os.listdir(bot_settings.LOCAL_DATA_DEBUG_DIR):
            file_path = os.path.join(bot_settings.LOCAL_DATA_DEBUG_DIR, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception:
                pass

        # JSON information has been completed at this point.
        # We now want to retrieve our two log files (last session log, titandash log)
        # to include in the directory of information.
        if session.count() > 0:
            copy(src=session.first().log.log_file, dst=bot_settings.LOCAL_DATA_DEBUG_DIR)
        if os.path.exists(bot_settings.LOCAL_DATA_LOG_FILE):
            copy(src=bot_settings.LOCAL_DATA_LOG_FILE, dst=bot_settings.LOCAL_DATA_DEBUG_DIR)

        # Looping through available windows, if any are present, take a screenshot
        # and include in our debug report.
        wh = WindowHandler()
        wh.enum()

        for hwnd, window in wh.filter().items():
            window.screenshot().save(fp=os.path.join(bot_settings.LOCAL_DATA_DEBUG_DIR, "{text}_{hwnd}.png".format(
                text=slugify(window.text),
                hwnd=window.hwnd
            )))

        # Finally, dump our data object into a file as well.
        with open(bot_settings.LOCAL_DATA_DEBUG_FILE, "w") as f:
            json.dump(data, f, cls=DecimalEncoder)

        # Once finished, ensure we open up the local data directory
        # so the user can view the new data or ideally, send it to us!
        subprocess.Popen('explorer "{debug_dir}"'.format(debug_dir=settings.LOCAL_DATA_DEBUG_DIR))
