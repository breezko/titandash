from django.shortcuts import render
from django.http.response import JsonResponse

from titandash.utils import start, pause, stop, resume, title
from titandash.utils import WindowHandler
from titandash.constants import RUNNING, PAUSED, STOPPED
from titandash.models.bot import BotInstance
from titandash.models.statistics import Session, Statistics, Log, ArtifactStatistics
from titandash.models.clan import RaidResult
from titandash.models.artifact import Artifact
from titandash.models.configuration import Configuration, ThemeConfig
from titandash.models.prestige import Prestige
from titandash.models.queue import Queue
from titandash.bot.core.constants import QUEUEABLE_FUNCTIONS, QUEUEABLE_TOOLTIPS, SHORTCUT_FUNCTIONS, WINDOW_FILTER

from io import BytesIO

import datetime
import base64
import json


def dashboard(request):
    """Main dashboard view."""
    ctx = {
        "configurations": [],
        "windows": [],
        "queueable": []
    }

    # Grab all configurations present to send to the dashboard.
    for config in Configuration.objects.all():
        ctx["configurations"].append({"id": config.pk, "name": config.name})

    wh = WindowHandler()
    wh.enum()
    for hwnd, window in wh.filter(contains=WINDOW_FILTER).items():
        ctx["windows"].append(window.json())

    ctx["windows"].reverse()

    # Grab all queueable functions.
    for queue in QUEUEABLE_FUNCTIONS:
        ctx["queueable"].append({
            "name": title(queue),
            "func": queue,
            "tooltip": QUEUEABLE_TOOLTIPS[queue]
        })

    return render(request, "dashboard.html", context=ctx)


def theme_change(request):
    selected = request.GET.get("theme")
    if not selected:
        selected = "default"

    theme = ThemeConfig.objects.grab()
    theme.theme = selected
    theme.save()

    return JsonResponse(data={"status": "success", "message": "Theme was successfully changed to {theme}".format(theme=theme.theme)})


def log(request, pk):
    """Retrieve a particular log file for viewing."""
    ctx = {
        "log": Log.objects.get(pk=pk).json()
    }

    return render(request, "log.html", context=ctx)


def session(request, uuid):
    """Retrieve a particular session."""
    ctx = {
        "session": Session.objects.get(uuid=uuid).json(),
    }

    ctx["SESSION_JSON"] = json.dumps(ctx)

    return render(request, "sessions/session.html", context=ctx)


def sessions(request):
    """Retrieve all sessions."""
    ctx = {"sessions": []}

    for s in Session.objects.all():
        ctx["sessions"].append(s.json())

    ctx["SESSIONS_JSON"] = json.dumps(ctx)

    return render(request, 'sessions/sessions.html', context=ctx)


def statistics(request):
    stats = Statistics.objects.grab()
    ctx = {"game_statistics": {title(key): value for key, value in stats.game_statistics.json().items()},
           "bot_statistics": {title(key): value for key, value in stats.bot_statistics.json().items()},
           "STATISTICS_JSON": json.dumps({
               "game_statistics": stats.game_statistics.json(),
               "bot_statistics": stats.bot_statistics.json()
           })}

    return render(request, "allStatistics.html", context=ctx)


def project_settings(request):
    """Main project settings view."""
    return render(request, "projectSettings.html")


def shortcuts(request):
    """View all shortcuts available for use with the bot."""
    ctx = {"shortcuts": {title(k): v.split("+") for k, v in SHORTCUT_FUNCTIONS.items()}}
    return render(request, "shortcuts.html", context=ctx)


def artifacts(request):
    """Retrieve all artifacts owned."""
    ctx = {"artifacts": []}
    for artifact_owned in ArtifactStatistics.objects.grab().artifacts.all():
        ctx["artifacts"].append(artifact_owned.json())

    ctx["artifactsTotalValue"] = Artifact.objects.all().count()
    ctx["artifactsOwnedValue"] = ArtifactStatistics.objects.grab().artifacts.filter(owned=True).count()

    ctx["ARTIFACTS_JSON"] = json.dumps(ctx)

    return render(request, "allArtifacts.html", context=ctx)


def all_prestiges(request):
    """Retrieve all prestiges present."""
    total_seconds = 0
    total_stages = 0
    ctx = {"prestiges": [], "avgPrestigeDuration": None, "avgPrestigeStage": None, "totalPrestiges": None}
    p = Prestige.objects.all().order_by("-timestamp")

    p_valid_time = p.filter(time__isnull=False)
    p_valid_time_cnt = len(p_valid_time)

    p_valid_stage = p.filter(stage__isnull=False)
    p_valid_stage_cnt = len(p_valid_stage)

    if len(p_valid_time) == 0:
        p_valid_time_cnt = 1
    if len(p_valid_stage) == 0:
        p_valid_stage_cnt = 1

    for prestige in p:
        ctx["prestiges"].append(prestige.json())

    for prestige in p_valid_time:
        total_seconds += prestige.time.total_seconds()
    for prestige in p_valid_stage:
        total_stages += prestige.stage

    if len(p) == 0:
        ctx["avgPrestigeDuration"] = "00:00:00"
        ctx["avgPrestigeStage"] = 0
    else:
        ctx["avgPrestigeDuration"] = str(datetime.timedelta(seconds=int(total_seconds / p_valid_time_cnt)))
        ctx["avgPrestigeStage"] = int(total_stages / p_valid_stage_cnt)

    ctx["totalPrestiges"] = p.count()
    ctx["PRESTIGES_JSON"] = json.dumps(ctx)

    return render(request, "allPrestiges.html", context=ctx)


def instance(request):
    return JsonResponse(data=BotInstance.objects.grab().json())


def kill_instance(request):
    bot = BotInstance.objects.grab()
    if bot.state == RUNNING or bot.state == PAUSED:
        stop()
        bot.stop()
        return JsonResponse(data={"status": "success", "message": "BotInstance has been stopped..."})

    return JsonResponse(data={"status": "success", "message": "No BotInstance is active to be stopped..."})


def signal(request):
    bot = BotInstance.objects.grab()
    sig = request.GET.get("signal")
    cfg = request.GET.get("config")
    win = request.GET.get("window")

    if sig == "PLAY":
        if bot.state == RUNNING:
            return JsonResponse(data={"status": "warning", "message": "BotInstance is already running..."})
        if bot.state == STOPPED:
            start(config=cfg, window=win)
            return JsonResponse(data={"status": "success", "message": "BotInstance has been started..."})
        if bot.state == PAUSED:
            resume()
            return JsonResponse(data={"status": "success", "message": "BotInstance has been resumed..."})

    if sig == "PAUSE":
        if bot.state == RUNNING:
            pause()
            return JsonResponse(data={"status": "success", "message": "PAUSE Signal has been received by the bot..."})
        if bot.state == STOPPED or bot.state == PAUSED:
            return JsonResponse(data={"status": "warning", "message": "BotInstance is not currently running..."})

    if sig == "STOP":
        if bot.state == RUNNING:
            stop()
            return JsonResponse(data={"status": "success", "message": "STOP Signal has been received by the bot..."})
        if bot.state == STOPPED or bot.state == PAUSED:
            return JsonResponse(data={"status": "warning", "message": "BotInstance is not currently running..."})


def prestiges(request):
    """Grab any prestige instances that are associated with the specified session."""
    # GET.
    typ = request.GET.get("type")
    if typ == "PRESTIGES":
        _session = request.GET.get("session")

        if session:
            p = Prestige.objects.filter(session__uuid=_session)
        else:
            p = Prestige.objects.all()

        # Parse out filtered data...
        # Prestige data as well as averaged out data (average stage prestige, average time per prestige).
        dct = {
            "prestiges": [],
            "avgPrestigeTime": None,
            "avgPrestigeStage": None,
            "lastArtifact": None,
            "totalPrestiges": len(p)
        }

        lst = []
        if len(p) > 0:
            total_times = 0
            total_stages = 0
            for prestige in p.order_by("-timestamp"):
                total_times += prestige.time.total_seconds() if prestige.time else 0
                total_stages += prestige.stage if prestige.stage else 0
                lst.append(prestige.json())

            # Assign all prestiges to data dictionary.
            dct["avgPrestigeTime"] = str(datetime.timedelta(seconds=int(total_times / len(p))))
            dct["avgPrestigeStage"] = int(total_stages / len(p))
            dct["prestiges"] = lst
            dct["lastArtifact"] = p.last().artifact.json()

        return JsonResponse(data=dct)

    if typ == "AVG":
        seconds = int(request.GET.get("totalSeconds"))
        valid_seconds = int(request.GET.get("validSeconds"))
        stages = int(request.GET.get("totalStages"))
        valid_stages = int(request.GET.get("validStages"))

        if valid_seconds == 0:
            valid_seconds = 1
        if valid_stages == 0:
            valid_stages = 1

        return JsonResponse(data={
            "avgPrestigeTime": str(datetime.timedelta(seconds=int(seconds / valid_seconds))),
            "avgPrestigeStage": int(stages / valid_stages)
        })


def screen(request):
    """Grab a screen shot of the current bot in game... Returning it as Base64 Image."""
    # Note: Nox Emulator is the only supported emulator... We can use
    # the expected values for that emulator for our screenshots...
    from titandash.bot.external.imagesearch import region_grabber
    from PIL.Image import ANTIALIAS

    inst = BotInstance.objects.grab()
    window = inst.window

    grab = region_grabber((
        window["x"], window["y"],
        window["x"] + window["width"],
        window["y"] + window["height"]
    ))
    grab = grab.resize((360, 600), ANTIALIAS)

    buffered = BytesIO()
    grab.save(buffered, format="JPEG", quality=30)

    b = base64.b64encode(buffered.getvalue())
    image_str = "data:image/jpeg;base64, {b64}".format(b64=b.decode("utf-8"))
    return JsonResponse(data={"src": image_str})


def generate_queued(request):
    """Generate a queued function representing the function specified by the user."""
    func = request.GET.get("function")
    Queue.objects.create(function=func)

    return JsonResponse(data={"status": "success", "function": title(func)})


def raids(request):
    ctx = {"raids": []}
    for raid_result in RaidResult.objects.all().order_by("parsed"):
        ctx["raids"].append(raid_result.json())

    ctx["RAIDS_JSON"] = json.dumps(ctx)

    return render(request, "raids/raids.html", context=ctx)


def raid(request, digest):
    ctx = {
        "raid": RaidResult.objects.get(digest=digest).json()
    }

    ctx["RAID_JSON"] = json.dumps(ctx)

    return render(request, "raids/raid.html", context=ctx)
