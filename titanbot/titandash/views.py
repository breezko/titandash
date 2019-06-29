from django.shortcuts import render
from django.http.response import JsonResponse

from titandash.utils import start, pause, stop, resume, title
from titandash.constants import RUNNING, PAUSED, STOPPED
from titandash.models.token import Token
from titandash.models.bot import BotInstance
from titandash.models.statistics import Session, Statistics, Log, ArtifactStatistics
from titandash.models.artifact import Artifact
from titandash.models.configuration import Configuration
from titandash.models.prestige import Prestige
from titandash.models.queue import Queue
from titandash.bot.core.bot import QUEUEABLE_FUNCTIONS, QUEUEABLE_TOOLTIPS
from titandash.bot.core.authentication.auth import Authenticator

from io import BytesIO

import datetime
import base64
import json


def dashboard(request):
    """Main dashboard view."""
    ctx = {
        "configurations": []
    }

    # Grab all configurations present to send to the dashboard.
    for config in Configuration.objects.all():
        ctx["configurations"].append({"id": config.pk, "name": config.name})

    # Grab all queueable functions.
    ctx["queueable"] = []
    for queue in QUEUEABLE_FUNCTIONS:
        ctx["queueable"].append({
            "name": title(queue),
            "func": queue,
            "tooltip": QUEUEABLE_TOOLTIPS[queue]
        })

    return render(request, "dashboard.html", context=ctx)


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

    for prestige in p:
        total_seconds += prestige.time.total_seconds()
        total_stages += prestige.stage if prestige.stage else 0
        ctx["prestiges"].append(prestige.json())

    if len(p) == 0:
        ctx["avgPrestigeDuration"] = "00:00:00"
        ctx["avgPrestigeStage"] = 0
    else:
        ctx["avgPrestigeDuration"] = str(datetime.timedelta(seconds=int(total_seconds / len(p))))
        ctx["avgPrestigeStage"] = int(total_stages / len(p))

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

    if sig == "PLAY":
        if bot.state == RUNNING:
            return JsonResponse(data={"status": "warning", "message": "BotInstance is already running..."})
        if bot.state == STOPPED:
            start(config=cfg)
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
        session = request.GET.get("session")

        if session:
            p = Prestige.objects.filter(session__uuid=session)
        else:
            p = Prestige.objects.all()

        p = p.order_by("timestamp")

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
                total_times += prestige.time.total_seconds()
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
        stages = int(request.GET.get("totalStages"))
        count = int(request.GET.get("totalPrestiges"))

        if count == 0:
            count = 1

        return JsonResponse(data={
            "avgPrestigeTime": str(datetime.timedelta(seconds=int(seconds / count))),
            "avgPrestigeStage": int(stages / count)
        })


def screen(request):
    """Grab a screen shot of the current bot in game... Returning it as Base64 Image."""
    # Note: Nox Emulator is the only supported emulator... We can use
    # the expected values for that emulator for our screenshots...
    from titandash.bot.core.maps import EMULATOR_PADDING_MAP
    from titandash.bot.external.imagesearch import region_grabber
    from PIL.Image import ANTIALIAS

    height = 800
    width = 480

    x = 0
    y = 0

    x2 = width + x + EMULATOR_PADDING_MAP["nox"]["x"]
    y2 = height + y + EMULATOR_PADDING_MAP["nox"]["y"]

    grab = region_grabber((x, y, x2, y2))
    grab = grab.resize((360, 600), ANTIALIAS)

    buffered = BytesIO()
    grab.save(buffered, format="JPEG", quality=10)

    b = base64.b64encode(buffered.getvalue())
    image_str = "data:image/jpeg;base64, {b64}".format(b64=b.decode("utf-8"))
    return JsonResponse(data={"src": image_str})


def generate_queued(request):
    """Generate a queued function representing the function specified by the user."""
    func = request.GET.get("function")
    Queue.objects.create(function=func)

    return JsonResponse(data={"status": "success", "function": title(func)})


def update_token(request):
    """Attempt to update the existing TokenInstance."""
    try:
        token = Token.objects.grab()
        token.token = request.GET.get("token")
        token.save()

        return JsonResponse(data={"status": "success", "message": "Token has been updated successfully..."})
    except Exception as exc:
        return JsonResponse(data={"status": "danger", "message": "An error occurred while saving token: {exc}".format(exc=exc)})


def flush_token(request):
    """Attempt to flush the current token."""
    token = Token.objects.grab()
    if token.token is None or token.token == "":
        return JsonResponse(data={"status": "warning", "message": "No valid token is present to flush."})

    # Retrieve an authentication instance used for tooling.
    try:
        response = Authenticator(token=token.token, tooled=True).terminate()
        if "status" not in response:
            return JsonResponse(data={"status": "warning", "message": str(response["detail"])})

        # If a successful token termination takes place... We also stop the current BotInstance.
        # this prevents users from starting the Bot, terminating their instance which would allow someone
        # else to use it.
        stop()

        return JsonResponse(data={"status": "success", "message": "Flush: {status}".format(status=response["status"])})
    except Exception as exc:
        return JsonResponse(data={"status": "danger", "message": str(exc)})
