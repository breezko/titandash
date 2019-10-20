"""
tester.py

Place any helpful functions or commands that can be used to actively test different parts of a instantiated Bot.
"""
from django.utils.timezone import now

from titandash.models.configuration import Configuration
from titandash.models.prestige import Prestige
from titandash.models.artifact import Artifact
from titandash.models.statistics import Session
from titandash.models.bot import BotInstance
from titandash.utils import WindowHandler
from titandash.bot.core.bot import Bot

from pynput.mouse import Listener, Button


from datetime import timedelta


def make_bot():
    """
    Create a Bot with the first available configuration object.

    Note: The bot is never started here, just instantiated, allowing you to call any function
          available on the Bot without looping through the main Bot loops.

    Usage:
    from titandash.bot.core.tester import *; bot = make_bot();
    from titandash.bot.core.tester import *; bot = make_bot(); bot.owned_artifacts = bot.get_upgrade_artifacts(); bot.next_artifact_index = 0; bot.update_next_artifact_upgrade()

    from titandash.bot.core.tester import *; bot = make_bot(); bot.owned_artifacts = bot.get_upgrade_artifacts(); bot.next_artifact_index = 0; bot.update_next_artifact_upgrade(); bot.setup_shortcuts();
    """
    wh = WindowHandler()
    wh.enum()

    return Bot(
        configuration=Configuration.objects.first(),
        window=next(iter(wh.filter().items()))[1],
        instance=BotInstance.objects.first(),
        start=False
    )


clicks = []


def record_clicks():
    """
    Record the clicks that take place on the screen.

    Each click coordinate is appended to a list of clicks and outputted once the
    user has decided to stop recording, which can by stopped by pressing the right mouse button.

    from titandash.bot.core.tester import *; record_clicks()
    """
    # Setup the events used by our listener.
    def on_click(x, y, button, pressed):
        global clicks
        if pressed and button == Button.left:
            clicks.append((x, y))
        if pressed and button == Button.right:
            print("CLICKS:")
            for click in clicks:
                print(click)

            # Reset clicks list to blank.
            clicks = []

    print("RECORDING CLICKS NOW...")
    with Listener(on_click=on_click) as listener:
        listener.join()


def fix_clicks(fix_x=0, fix_y=34):
    """
    Given a set of tuple points (X, Y), fix the locations by subtracting the given amount from the
    x and y axis.

    from titandash.bot.core.tester import *; fix_clicks()
    """
    bot = make_bot()

    new_locs = ()
    for point in bot.locs.flash_zip:
        new_locs += ((point[0] - fix_x, point[1] - fix_y,),)

    print(new_locs)


def make_prestige(instance_id=None, session_uuid=None):
    """
    Generate a generic prestige instance.

    This is useful for testing the websocket functionality used by the dashboard.
    Multiple session support requires prestiges to show up based on the instance they are generated for.

    from titandash.bot.core.tester import *; make_prestige(instance_id=1);
    """
    timestamp = now()
    time = timedelta(minutes=30)
    stage = 55000
    artifact = Artifact.objects.first()
    session = Session.objects.get(uuid=session_uuid) if session_uuid else Session.objects.first()
    instance = BotInstance.objects.get(pk=instance_id) if instance_id else BotInstance.objects.grab()

    return Prestige.objects.create(
        timestamp=timestamp,
        time=time,
        stage=stage,
        artifact=artifact,
        session=session,
        instance=instance
    )
