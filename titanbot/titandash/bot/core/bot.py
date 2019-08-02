"""
core.py

Main bot initialization and script startup should take place here. All actions and main bot loops
will be maintained from this location.
"""
from settings import STAGE_CAP, GAME_VERSION, BOT_VERSION, GIT_COMMIT

from django.utils import timezone

from titandash.models.bot import BotInstance
from titandash.models.queue import Queue
from titandash.models.clan import Clan, RaidResult

from .maps import *
from .constants import (
    STAGE_PARSE_THRESHOLD, FUNCTION_LOOP_TIMEOUT, BOSS_LOOP_TIMEOUT,
    QUEUEABLE_FUNCTIONS, FORCEABLE_FUNCTIONS
)
from .grabber import Grabber
from .stats import Stats
from .wrap import Images, Locs, Colors
from .utilities import click_on_point, click_on_image, drag_mouse, make_logger, strfdelta, sleep
from .decorators import not_in_transition, wait_afterwards
from .shortcuts import ShortcutListener

from pyautogui import easeOutQuad, FailSafeException

import datetime
import random
import keyboard
import win32clipboard


class NoTokenException(Exception):
    pass


class TerminationEncountered(Exception):
    pass


class Bot:
    """
    Main Bot Class.

    Initial setup is handled here, as well as some data setup for use during runtime.

    Statistics, Configurations and Logging is all setup here. Database values are grabbed and used
    in real time to allow for updates to the configuration while the bot is still running.
    """
    def __init__(self, configuration, logger=None, start=False):
        """
        Initialize a new Bot. Setting up base variables as well as performing some bootstrapping
        to ensure authentication is handled before moving on.
        """
        self.TERMINATE = False
        self.PAUSE = False
        self.ERRORS = 0
        self.ADVANCED_START = None
        self.configuration = configuration
        self.instance = BotInstance.objects.grab()
        self.instance.configuration = configuration
        self.instance.errors = self.ERRORS

        # Initial property instance attributes. These are confined to their properties/setters
        # defined below.
        self.current_stage = None
        self.current_function = None
        self.next_action_run = None
        self.next_prestige = None
        self.next_stats_update = None
        self.next_recovery_reset = None
        self.next_daily_achievement_check = None
        self.next_clan_results_parse = None
        self.next_heavenly_strike = None
        self.next_deadly_strike = None
        self.next_hand_of_midas = None
        self.next_fire_sword = None
        self.next_war_cry = None
        self.next_shadow_clone = None

        if logger:
            self.logger = logger
        else:
            self.logger = make_logger(self.configuration.logging_level, log_file=None)

        if not self.configuration.enable_logging:
            self.logger.disabled = True

        # Bot utilities.
        self.grabber = Grabber(self.configuration.emulator, self.logger)
        self.stats = Stats(grabber=self.grabber, configuration=self.configuration, logger=self.logger)

        # Statistics handles Log instance creation... Set BotInstance now.
        self.instance.log = self.stats.session.log

        # Data containers.
        self.images = Images(IMAGES, self.logger)
        self.locs = Locs(GAME_LOCS, self.logger)
        self.colors = Colors(GAME_COLORS, self.logger)

        self._last_stage = None
        self._current_stage = None
        self._current_function = None

        self._next_action_run = None
        self._next_prestige = None
        self._next_stats_update = None
        self._next_recovery_reset = None
        self._next_daily_achievement_check = None
        self._next_clan_results_parse = None

        self._next_heavenly_strike = None
        self._next_deadly_strike = None
        self._next_hand_of_midas = None
        self._next_fire_sword = None
        self._next_war_cry = None
        self._next_shadow_clone = None

        self.instance.start(session=self.stats.session)

        self.logger.info("=======================================================")
        self.logger.info("Bot (v{version}) (v{game_version}) [{commit}] has been initialized.".format(version=BOT_VERSION, game_version=GAME_VERSION, commit=GIT_COMMIT[:10]))
        self.logger.info("[{session}]".format(session=str(self.stats.session)))
        self.logger.info("=======================================================")

        # Create a list of the functions called in there proper order
        # when actions are performed by the bot.
        self.action_order = self._order_actions()
        self.skill_order = self._order_skill_intervals()

        # Store information about the artifacts in game.
        self.owned_artifacts = None
        self.next_artifact_index = None
        self.next_artifact_upgrade = None

        # Setup the datetime objects used initially to determine when the bot
        # will perform specific actions in game.
        self.calculate_skill_execution()
        self.calculate_next_prestige()
        self.calculate_next_stats_update()
        self.calculate_next_action_run()
        self.calculate_next_recovery_reset()
        self.calculate_next_daily_achievement_check()
        self.calculate_next_clan_result_parse()

        if start:
            self.run()

    # Setup Instance/Attr Setters.
    @property
    def current_stage(self):
        return self._current_stage

    @current_stage.setter
    def current_stage(self, value):
        self._current_stage = value
        self.instance.current_stage = value
        self.instance.save()

    @property
    def current_function(self):
        return self._current_function

    @current_function.setter
    def current_function(self, value):
        self._current_function = value
        self.instance.current_function = value
        self.instance.save()

    @property
    def next_action_run(self):
        return self._next_action_run

    @next_action_run.setter
    def next_action_run(self, value):
        self._next_action_run = value
        self.instance.next_action_run = value
        self.instance.save()

    @property
    def next_prestige(self):
        return self._next_prestige

    @next_prestige.setter
    def next_prestige(self, value):
        self._next_prestige = value
        self.instance.next_prestige = value
        self.instance.save()

    @property
    def next_stats_update(self):
        return self._next_stats_update

    @next_stats_update.setter
    def next_stats_update(self, value):
        self._next_stats_update = value
        self.instance.next_stats_update = value
        self.instance.save()

    @property
    def next_recovery_reset(self):
        return self._next_recovery_reset

    @next_recovery_reset.setter
    def next_recovery_reset(self, value):
        self._next_recovery_reset = value
        self.instance.next_recovery_reset = value
        self.instance.save()

    @property
    def next_daily_achievement_check(self):
        return self._next_daily_achievement_check

    @next_daily_achievement_check.setter
    def next_daily_achievement_check(self, value):
        self._next_daily_achievement_check = value
        self.instance.next_daily_achievement_check = value
        self.instance.save()

    @property
    def next_clan_results_parse(self):
        return self._next_clan_results_parse

    @next_clan_results_parse.setter
    def next_clan_results_parse(self, value):
        self._next_clan_results_parse = value
        self.instance.next_clan_results_parse = value
        self.instance.save()

    @property
    def next_heavenly_strike(self):
        return self._next_heavenly_strike

    @next_heavenly_strike.setter
    def next_heavenly_strike(self, value):
        self._next_heavenly_strike = value
        self.instance.next_heavenly_strike = value
        self.instance.save()

    @property
    def next_deadly_strike(self):
        return self._next_deadly_strike

    @next_deadly_strike.setter
    def next_deadly_strike(self, value):
        self._next_deadly_strike = value
        self.instance.next_deadly_strike = value
        self.instance.save()

    @property
    def next_hand_of_midas(self):
        return self._next_deadly_strike

    @next_hand_of_midas.setter
    def next_hand_of_midas(self, value):
        self._next_hand_of_midas = value
        self.instance.next_hand_of_midas = value
        self.instance.save()

    @property
    def next_fire_sword(self):
        return self._next_deadly_strike

    @next_fire_sword.setter
    def next_fire_sword(self, value):
        self._next_fire_sword = value
        self.instance.next_fire_sword = value
        self.instance.save()

    @property
    def next_war_cry(self):
        return self._next_deadly_strike

    @next_war_cry.setter
    def next_war_cry(self, value):
        self._next_war_cry = value
        self.instance.next_war_cry = value
        self.instance.save()

    @property
    def next_shadow_clone(self):
        return self._next_deadly_strike

    @next_shadow_clone.setter
    def next_shadow_clone(self, value):
        self._next_shadow_clone = value
        self.instance.next_shadow_clone = value
        self.instance.save()

    def get_upgrade_artifacts(self, testing=False):
        """
        Retrieve a list of all discovered/owned artifacts in game that will be iterated over
        and upgraded throughout runtime.

        The testing boolean is used to ignore the owned filter so all artifacts will be grabbed
        and can be tested thoroughly.
        """
        self.logger.info("Retrieving owned artifacts that will be used when upgrading after prestige.")
        lst = []

        # Grabbing all configuration values used to determine which artifacts are
        # upgraded when called.
        upgrade_tiers = self.configuration.upgrade_owned_tier.all()
        ignore_artifacts = self.configuration.ignore_artifacts.all()
        upgrade_artifacts = self.configuration.upgrade_artifacts.all()
        if len(upgrade_tiers) > 0:
                upgrade_tiers = upgrade_tiers.values_list("tier", flat=True)
        if len(ignore_artifacts) > 0:
                ignore_artifacts = ignore_artifacts.values_list("name", flat=True)
        if len(upgrade_artifacts) > 0:
                upgrade_artifacts = upgrade_artifacts.values_list("name", flat=True)

        if testing:
            artifacts = self.stats.artifact_statistics.artifacts.all()
        else:
            artifacts = self.stats.artifact_statistics.artifacts.filter(owned=True)

        for artifact in artifacts.exclude(artifact__name__in=ARTIFACT_WITH_MAX_LEVEL):
            if artifact.artifact.name in ignore_artifacts:
                continue
            if artifact.artifact.tier.tier in upgrade_tiers or artifact.artifact.name in upgrade_artifacts:
                lst.append(artifact.artifact.name)
                self.logger.info("{artifact} WILL be upgraded".format(artifact=artifact))
                continue

        if len(lst) == 0:
            self.logger.error("No owned artifacts could be found... You must parse artifacts before beginning...")
            self.logger.info("Attempting to parse artifacts now...")
            self.parse_artifacts()
            lst = self.get_upgrade_artifacts()

            if len(lst) == 0:
                self.logger.error("No artifacts were parsed... Disabling artifact purchase for this session.")
                self.configuration.enable_artifact_purchase = False

        if self.configuration.shuffle_artifacts:
            self.logger.info("SHUFFLING artifacts that should be upgraded")
            random.shuffle(lst)

        self.logger.info("Next ARTIFACT UPGRADE: {artifact}".format(artifact=lst[0]))
        return lst

    def update_next_artifact_upgrade(self):
        """Update the next artifact to be upgraded to the next one in the list."""
        if self.next_artifact_index == len(self.owned_artifacts):
            self.next_artifact_index = 0

        self.next_artifact_upgrade = self.owned_artifacts[self.next_artifact_index]
        self.next_artifact_index += 1

        self.instance.next_artifact_upgrade = self.next_artifact_upgrade
        self.instance.save()

        self.logger.info("Next artifact_upgrade: {artifact}".format(artifact=self.next_artifact_upgrade))

    def parse_advanced_start(self, stage_text):
        """Attempt to parse out the advanced start stage value into a valid integer."""
        try:
            stage = int(stage_text)
            self.logger.info("Advanced start stage: {stage_text} was successfully coerced into an integer: {stage}".format(stage_text=stage_text, stage=stage))

            if stage > STAGE_CAP:
                self.logger.info("Stage: {stage} is > the STAGE CAP: {stage_cap}, resetting advanced start".format(stage=stage, stage_cap=STAGE_CAP))
                self.ADVANCED_START = None
                return

            self.logger.info("Current advanced start in game was successfully parsed: {stage}".format(stage=stage))
            self.ADVANCED_START = stage

        except ValueError:
            self.logger.error("OCR check could not parse out a proper string from image, resetting advanced start value.")
            self.ADVANCED_START = None

    def parse_current_stage(self):
        """
        Attempt to update the current stage attribute through an OCR check in game. The current_stage
        attribute is initialized as None, and if the current stage parsed here is unable to be coerced into
        an integer, it will be set back to None.

        When using the attribute, a check should be performed to ensure it isn't None before running
        numeric friendly conditionals.
        """
        stage_parsed = self.stats.stage_ocr()
        try:
            stage = int(stage_parsed)
            self.logger.info("Stage '{stage_text}' successfully coerced into an integer: {stage}.".format(stage_text=stage_parsed, stage=stage))
            if stage > STAGE_CAP:
                self.logger.info("Stage {stage} is > the STAGE_CAP: {stage_cap}, resetting stage variables.".format(stage=stage, stage_cap=STAGE_CAP))
                return

            if self.ADVANCED_START:
                if stage < self.ADVANCED_START:
                    self.logger.info("Stage: {stage} is < the ADVANCED START: {advanced_start}, leaving current stage unchanged".format(stage=stage, advanced_start=self.ADVANCED_START))
                    return

            # Is the stage potentially way greater than the last check? Could mean the parse failed.
            if isinstance(self._last_stage, int):
                diff = stage - self._last_stage
                if diff > STAGE_PARSE_THRESHOLD:
                    self.logger.info(
                        "Difference between current stage and last stage passes the stage change threshold: "
                        "{stage_thresh} ({stage} - {last_stage} = {diff}), resetting stage variables.".format(
                            stage_thresh=STAGE_PARSE_THRESHOLD, stage=stage, last_stage=self._last_stage, diff=diff))

                    self._last_stage, self.current_stage = None, None
                    return

            self.logger.info("Current stage in game was successfully parsed: {stage}".format(stage=stage))
            self._last_stage = self.current_stage
            self.logger.info("Last stage has been set to the previous current stage in game: {last_stage}".format(last_stage=self._last_stage))
            self.current_stage = stage

        # ValueError when the parsed stage isn't able to be coerced.
        except ValueError:
            self.logger.error("OCR check could not parse out a proper string from image, leaving stage variables as they were before...")
            self.logger.info("Current Stage: {current}".format(current=self.current_stage))
            self.logger.info("Last Stage: {last}".format(last=self._last_stage))
            self._last_stage, self.current_stage = None, None

    def _order_actions(self):
        """Determine order of in game actions. Mapped to their respective functions."""
        sort = sorted([
            (self.configuration.order_level_heroes, self.level_heroes, "level_heroes"),
            (self.configuration.order_level_master, self.level_master, "level_master"),
            (self.configuration.order_level_skills, self.level_skills, "level_skills"),
        ], key=lambda x: x[0])

        self.logger.info("Actions in game have been ordered successfully.")
        for action in sort:
            self.logger.info("{order} : {action_key}.".format(order=action[0], action_key=action[2]))

        return sort

    def _order_skill_intervals(self):
        """Determine order of skills with intervals, first index will be the longest interval."""
        sort = sorted([
            (self.configuration.interval_heavenly_strike, "heavenly_strike"),
            (self.configuration.interval_deadly_strike, "deadly_strike"),
            (self.configuration.interval_fire_sword, "hand_of_midas"),
            (self.configuration.interval_fire_sword, "fire_sword"),
            (self.configuration.interval_shadow_clone, "war_cry"),
            (self.configuration.interval_shadow_clone, "shadow_clone"),
        ], key=lambda x: x[0], reverse=True)

        self.logger.info("Skill intervals have been ordered successfully.")
        for index, skill in enumerate(sort, start=1):
            self.logger.info("{index}: {key} ({interval})".format(index=index, key=skill[1], interval=skill[0]))

        return sort

    @not_in_transition
    def _inactive_skills(self):
        """Create a list of all skills that are currently inactive."""
        inactive = []
        for key, region in MASTER_COORDS["skills"].items():
            if self.grabber.search(self.images.cancel_active_skill, region, bool_only=True):
                continue
            inactive.append(key)

        for key in inactive:
            self.logger.info("{key} is not currently activated.".format(key=key))

        return inactive

    @not_in_transition
    def _not_maxed(self, inactive):
        """Given a list of inactive skill keys, determine which ones are not maxed."""
        not_maxed = []
        for key, region in {k: r for k, r in MASTER_COORDS["skills"].items() if k in inactive}.items():
            if self.grabber.search(self.images.skill_max_level, region, bool_only=True):
                continue
            not_maxed.append(key)

        for key in not_maxed:
            self.logger.info("{key} is not currently max level.".format(key=key))

        return not_maxed

    def calculate_skill_execution(self):
        """Calculate the datetimes that are attached to each skill in game and when they should be activated."""
        now = timezone.now()
        for key in SKILLS:
            interval_key = "interval_{0}".format(key)
            next_key = "next_{0}".format(key)
            interval = getattr(self.configuration, interval_key, 0)
            if interval != 0:
                dt = now + datetime.timedelta(seconds=interval)
                setattr(self, next_key, dt)
                self.logger.info("{skill} will be activated in {time}.".format(skill=key, time=strfdelta(dt - now)))
            else:
                self.logger.info("{skill} has interval set to zero, will not be activated.".format(skill=key))

    def calculate_next_prestige(self):
        """Calculate when the next timed prestige will take place."""
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.prestige_x_minutes * 60)
        self.next_prestige = dt
        self.logger.info("The next timed prestige will take place in {time}".format(time=strfdelta(dt - now)))

    def calculate_next_recovery_reset(self):
        """Calculate when the next recovery reset will take place."""
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.recovery_check_interval_minutes * 60)
        self.next_recovery_reset = dt
        self.logger.info("The next recovery reset will take place in {time}".format(time=strfdelta(dt - now)))

    def recover(self, force=False):
        """
        Begin the process to recover the game if necessary.

        Recovering the game requires the following steps:
            - Press the exit button within the Nox emulator.
            - Press the 'exit and restart' button within Nox.
            - Wait for a decent amount of time for the emulator to start.
            - Find the TapTitans2 app icon.
            - Start TapTitans2 and wait for a while for the game to start.
        """
        if self.ERRORS >= self.configuration.recovery_allowed_failures or force:
            # Too many errors have occurred... Resetting the count and attempting to completely
            # restart TapTitans 2.
            self.ERRORS = 0
            if force:
                self.logger.info("Forcing an in game recovery now and attempting to restart the game.")
            else:
                self.logger.info("{amount} errors have occurred before a reset, attempting to restart the game now...".format(amount=self.ERRORS))

            sleep(3)
            # Restart the emulator and wait for a while for it to boot up...
            self.logger.info("Attempting to restart the emulator...")
            click_on_point(EMULATOR_LOCS[self.configuration.emulator]["close_emulator"], pause=1)

            while self.grabber.search(self.images.restart, bool_only=True):
                found, pos = self.grabber.search(self.images.restart)
                if found:
                    self.logger.info("Restarting Emulator Now...")
                    click_on_image(self.images.restart, pos, pause=2)

            self.logger.info("Waiting For TapTitans2 Launcher To Become Available...")
            while not self.grabber.search(self.images.tap_titans_2, bool_only=True):
                self.logger.info("Couldn't find TapTitans2... Waiting and trying again.")
                sleep(2)

            found, pos = self.grabber.search(self.images.tap_titans_2)
            if found:
                self.logger.info("TapTitans2 was found, starting game now...")
                click_on_image(self.images.tap_titans_2, pos, pause=40)

            self.calculate_next_recovery_reset()
            return

        # Otherwise, determine if the error counter should be reset at this point.
        # To ensure an un-necessary recovery doesn't take place.
        else:
            now = timezone.now()
            if now > self.next_recovery_reset:
                self.logger.info("{amount}/{needed} errors occurred before reset, recovery will not take place.".format(amount=self.ERRORS, needed=self.configuration.recovery_allowed_failures))
                self.logger.info("Resetting error count now...")
                self.ERRORS = 0
                self.calculate_next_recovery_reset()

    def should_prestige(self):
        """
        Determine if prestige will take place. This value is based off of the configuration
        specified by the User.

        - After specified amount of time during run.
        - After a certain stage has been reached.
        - After max stage has been reached.
        - After a percent of max stage has been reached.
        """
        if self.configuration.prestige_x_minutes != 0:
            now = timezone.now()
            self.logger.info("Timed prestige is enabled, and should take place in {time}".format(time=strfdelta(self.next_prestige - now)))

            # Is the hard time limit set? If it is, perform prestige no matter what,
            # otherwise, look at the current stage conditionals present and prestige
            # off of those instead.
            if now > self.next_prestige:
                self.logger.debug("Timed prestige will happen now.")
                return True

        # Current stage must not be None, using time gate before this check. stage == None is only possible when
        # OCR checks are failing, this can happen when a stage change happens as the check takes place, causing
        # the image recognition to fail. OR if the parsed text doesn't pass the validation checks when parse is
        # malformed.
        if self.current_stage is None:
            self.logger.info("Current stage is currently None, no stage conditionals can be checked currently.")
            return False

        # Any other conditionals will be using the current stage attribute of the bot.
        elif self.configuration.prestige_at_stage != 0:
            self.logger.info("Prestige at specific stage: {current}/{needed}.".format(current=self.current_stage, needed=self.configuration.PRESTIGE_AT_STAGE))
            if self.current_stage >= self.configuration.prestige_at_stage:
                self.logger.info("Prestige stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        # These conditionals are dependant on the highest stage reached taken
        # from the bot's current game statistics.
        if self.configuration.prestige_at_max_stage:
            self.logger.info("Prestige at max stage: {current}/{needed}.".format(current=self.current_stage, needed=self.stats.highest_stage))
            if self.current_stage >= self.stats.highest_stage:
                self.logger.info("Max stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        elif self.configuration.prestige_at_max_stage_percent != 0:
            percent = float(self.configuration.prestige_at_max_stage_percent) / 100
            threshold = int(self.stats.highest_stage * percent)
            self.logger.info("Prestige at max stage percent ({percent}): {current}/{needed}".format(percent=percent, current=self.current_stage, needed=threshold))
            if self.current_stage >= threshold:
                self.logger.info("Percent of max stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        # Otherwise, only a time limit has been set for a prestige and it wasn't reached.
        return False

    def calculate_next_action_run(self):
        """Calculate when the next set of actions will be ran."""
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.run_actions_every_x_seconds)
        self.next_action_run = dt
        self.logger.info("Actions in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    def calculate_next_stats_update(self):
        """Calculate when the next stats update should take place."""
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.update_stats_every_x_minutes * 60)
        self.next_stats_update = dt
        self.logger.info("Statistics update in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    def calculate_next_daily_achievement_check(self):
        """Calculate when the next daily achievement check should take place."""
        now = timezone.now()
        dt = now + datetime.timedelta(hours=self.configuration.daily_achievements_check_every_x_hours)
        self.next_daily_achievement_check = dt
        self.logger.info("Daily achievement check in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    def calculate_next_clan_result_parse(self):
        """Calculate when the next clan result parse should take place."""
        if self.configuration.enable_clan_results_parse:
            now = timezone.now()
            dt = now + datetime.timedelta(minutes=self.configuration.parse_clan_results_every_x_minutes)
            self.next_clan_results_parse = dt
            self.logger.info("Clan results parse will be initiated in {time}".format(time=strfdelta(dt - now)))
        else:
            # If result parsing is disabled, No datetime is configured and will be ignored.
            self.next_clan_results_parse = None

    @not_in_transition
    def level_heroes(self):
        """Perform all actions related to the levelling of all heroes in game."""
        if self.configuration.enable_heroes:
            self.logger.info("Hero levelling process is beginning now.")
            if not self.goto_heroes(collapsed=False):
                return False

            # A quick check can be performed to see if the top of the heroes panel contains
            # a hero that is already max level, if this is the case, it's safe to assume
            # that all heroes below have been maxed out. Instead of scrolling and levelling
            # all heroes, just level the top heroes.
            if self.grabber.search(self.images.max_level, bool_only=True):
                self.logger.info("A max levelled hero has been found on the top portion of the hero panel.")
                self.logger.info("Only the first set of heroes will be levelled.")
                for point in HEROES_LOCS["level_heroes"][::-1][1:9]:
                    click_on_point(point, self.configuration.hero_level_intensity, interval=0.07)

                # Early exit as well.
                return

            # Always level the first 5 heroes in the list.
            self.logger.info("Levelling first five heroes in list.")
            for point in HEROES_LOCS["level_heroes"][::-1][1:6]:
                click_on_point(point, self.configuration.hero_level_intensity, interval=0.07)

            # Travel to the bottom of the panel.
            for i in range(5):
                drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end)

            drag_start = HEROES_LOCS["drag_heroes"]["start"]
            drag_end = HEROES_LOCS["drag_heroes"]["end"]

            # Begin level and scrolling process. An assumption is made that all heroes
            # are unlocked, meaning that some un-necessary scrolls may take place.
            self.logger.info("Scrolling and levelling all heroes.")
            for i in range(4):
                for point in HEROES_LOCS["level_heroes"]:
                    click_on_point(point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                # Skip the last drag since it's un-needed.
                if i != 3:
                    drag_mouse(drag_start, drag_end, duration=1, pause=1, tween=easeOutQuad, quick_stop=self.locs.scroll_quick_stop)

    @not_in_transition
    def level_master(self):
        """Perform all actions related to the levelling of the sword master in game."""
        if self.configuration.enable_master:
            self.logger.info("Levelling the sword master {clicks} time(s)".format(clicks=self.configuration.master_level_intensity))
            if not self.goto_master(collapsed=False):
                return False

            click_on_point(MASTER_LOCS["master_level"], clicks=self.configuration.master_level_intensity)

    @not_in_transition
    def level_skills(self):
        """Perform all actions related to the levelling of skills in game."""
        if self.configuration.enable_skills:
            self.logger.info("Levelling up skills in game if they are inactive and not maxed.")
            if not self.goto_master(collapsed=False):
                return False

            # Looping through each skill coord, clicking to level up.
            for skill in self._not_maxed(self._inactive_skills()):
                point = MASTER_LOCS["skills"].get(skill)

                # Should the bot upgrade the max amount of upgrades available for the current skill?
                if self.configuration.max_skill_if_possible:
                    # Retrieve the pixel location where the color should be the proper max level
                    # color once a single click takes place.
                    color_point = MASTER_LOCS["skill_level_max"].get(skill)
                    click_on_point(point, pause=1)

                    # Take a snapshot right after, and check for the point being the proper color.
                    self.grabber.snapshot()
                    if self.grabber.current.getpixel(color_point) == self.colors.WHITE:
                        self.logger.info("Levelling max amount of available upgrades for skill: {skill}.".format(skill=skill))
                        click_on_point(color_point, pause=0.5)

                # Otherwise, just level up the skills normally using the intensity setting.
                else:
                    self.logger.info("Levelling skill: {skill} {intensity} time(s).".format(skill=skill, intensity=self.configuration.skill_level_intensity))
                    click_on_point(MASTER_LOCS["skills"].get(skill), clicks=self.configuration.skill_level_intensity)

    def actions(self, force=False):
        """Perform bot actions in game."""
        now = timezone.now()
        if force or now > self.next_action_run:
            self.logger.info("{force_or_initiate} in game actions now.".format(force_or_initiate="Forcing" if force else "Beginning"))
            if not self.goto_master(collapsed=False):
                return

            for action in self.action_order:
                action[1]()

                # The end of each action should send the game back to the expanded
                # sword master panel, regardless of the order of actions to ensure
                # normalized instructions each time an action ends.
                self.goto_master(collapsed=False)

            # Recalculate the time for the next set of actions to take place.
            self.calculate_next_action_run()
            self.stats.statistics.bot_statistics.actions += 1
            self.stats.statistics.bot_statistics.save()

    @not_in_transition
    def update_stats(self, force=False):
        """Update the bot stats by travelling to the stats page in the heroes panel and performing OCR update."""
        if self.configuration.enable_stats:
            now = timezone.now()
            if force or now > self.next_stats_update:
                self.logger.info("{force_or_initiate} in game statistics update now.".format(force_or_initiate="Forcing" if force else "Beginning"))

                # Leaving boss fight here so that a stage transition does not take place
                # in the middle of a stats update.
                if not self.leave_boss():
                    return False

                # Sleeping slightly before attempting to goto top of heroes panel so that new hero
                # levels doesn't cause the 'top' of the panel to disappear after travelling.
                sleep(3)
                if not self.goto_heroes():
                    return False

                # Opening the stats panel within the heroes panel in game.
                # Scrolling to the bottom of this page, which contains all needed game stats info.
                click_on_point(HEROES_LOCS["stats_collapsed"], pause=0.5)
                for i in range(5):
                    drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end)

                self.stats.update_ocr()
                self.stats.statistics.bot_statistics.updates += 1
                self.stats.statistics.bot_statistics.save()

                self.calculate_next_stats_update()
                click_on_point(MASTER_LOCS["screen_top"], clicks=3)

    @not_in_transition
    def prestige(self, force=False):
        """Perform a prestige in game."""
        if self.configuration.enable_auto_prestige:
            if self.should_prestige() or force:
                self.logger.info("{begin_force} prestige process in game now.".format(begin_force="Beginning" if not force else "Forcing"))
                tournament = self.check_tournament()

                # If tournament==True, then a tournament was available to join (which means we prestiged, exit early).
                if tournament:
                    return False
                if not self.goto_master(collapsed=False, top=False):
                    return False

                # Click on the prestige button, and check for the prompt confirmation being present. Sleeping
                # slightly here to ensure that connections issues do not cause the prestige to be misfire.
                click_on_point(MASTER_LOCS["prestige"], pause=3)
                prestige_found, prestige_position = self.grabber.search(self.images.confirm_prestige)
                if prestige_found:
                    # Parsing the advanced start value that is present before a prestige takes place...
                    # This is used to improve stage parsing to not allow values < the advanced start value.
                    self.parse_advanced_start(self.stats.update_prestige(
                        artifact=self.next_artifact_upgrade, current_stage=self.current_stage))

                    click_on_point(MASTER_LOCS["prestige_confirm"], pause=1)
                    # Waiting for a while after prestiging, this reduces the chance
                    # of a game crash taking place due to many clicks while game is resetting.
                    click_on_point(MASTER_LOCS["prestige_final"], pause=35)

                    # If a timer is used for prestige. Reset this timer to the next timed prestige value.
                    if self.configuration.prestige_x_minutes != 0:
                        self.calculate_next_prestige()

                    # After a prestige, run all actions instantly to ensure that initial levels are gained.
                    # Also attempt to activate skills afterwards so that stage progression is started before
                    # any other actions or logic takes place in game.
                    self.actions(force=True)
                    self.activate_skills(force=True)

                    # If the current stage currently is greater than the current max stage, lets update our stats
                    # to reflect that a new max stage has been reached. This allows for
                    if self.current_stage and self.stats.highest_stage:
                            if self.current_stage > self.stats.highest_stage:
                                self.logger.info("Current run stage is greater than your previous max stage {max}, forcing a stats update to reflect these changes.".format(max=self.stats.highest_stage))
                                self.update_stats(force=True)

                    self.current_stage = self.ADVANCED_START

                    # Additional checks can take place during a prestige.
                    self.artifacts()
                    self.daily_rewards()
                    self.hatch_eggs()

    @not_in_transition
    def parse_artifacts(self):
        """Begin the process to parse owned artifacts from in game."""
        self.logger.info("Beginning artifact parsing process.")
        if not self.leave_boss():
            return False
        if not self.goto_artifacts(collapsed=False):
            return False

        # We are at the artifacts panel collapsed at this point... Begin parsing.
        self.stats.parse_artifacts()

    @not_in_transition
    def artifacts(self):
        """Determine whether or not any artifacts should be purchased, and purchase them."""
        if self.configuration.enable_artifact_purchase:
            self.logger.info("Beginning artifact purchase process.")
            if not self.goto_artifacts(collapsed=False):
                return False

            if self.configuration.upgrade_owned_artifacts:
                artifact = self.next_artifact_upgrade
                self.update_next_artifact_upgrade()

            # Fallback to the users first artifact. This shouldn't happen, better safe than sorry.
            else:
                artifact = self.owned_artifacts[0]

            self.logger.info("Attempting to upgrade {artifact} now.".format(artifact=artifact))

            # Make sure that the proper spend max multiplier is used to fully upgrade an artifact.
            # 1.) Ensure that the percentage (%) multiplier is selected.
            loops = 0
            while not self.grabber.search(self.images.percent_on, bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("Unable to set the artifact buy multiplier to use percentage, skipping.")
                    self.ERRORS += 1
                    return False

                click_on_point(ARTIFACTS_LOCS["percent_toggle"], pause=0.5)

            # 2.) Ensure that the SPEND Max multiplier is selected.
            loops = 0
            while not self.grabber.search(self.images.spend_max, bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("Unable to set the spend multiplier to SPEND Max, skipping for now.")
                    self.ERRORS += 1
                    return False

                click_on_point(ARTIFACTS_LOCS["buy_multiplier"], pause=0.5)
                click_on_point(ARTIFACTS_LOCS["buy_max"], pause=0.5)

            # Looking for the artifact to upgrade here, dragging until it is finally found.
            loops = 0
            while not self.grabber.search(ARTIFACT_MAP.get(artifact), bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("Artifact: {artifact} couldn't be found on screen, skipping for now for now.".format(artifact=artifact))
                    self.ERRORS += 1
                    return False

                drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end, quick_stop=self.locs.scroll_quick_stop)

            # Making it here means the artifact in question has been found.
            found, position = self.grabber.search(ARTIFACT_MAP.get(artifact))
            new_x = position[0] + ARTIFACTS_LOCS["artifact_push"]["x"]
            new_y = position[1] + ARTIFACTS_LOCS["artifact_push"]["y"]

            # Currently just upgrading the artifact to it's max level. Future updates may include the ability
            # to determine how much to upgrade an artifact by.
            click_on_point((new_x, new_y), pause=1)

    @not_in_transition
    def check_tournament(self):
        """Check that a tournament is available/active. Tournament will be joined if a new possible."""
        if self.configuration.enable_tournaments:
            self.logger.info("Checking for tournament ready to join/in progress.")
            if not self.goto_master():
                return False

            # Looping to find tournament here, since there's a chance that the tournament is finished, which
            # causes a star trail circle the icon. May be hard to find, give it a couple of tries.
            tournament_found = False
            for i in range(5):
                tournament_found, tournament_position = self.grabber.search(self.images.tournament)
                if tournament_found:
                    break

                # Wait slightly before trying again.
                sleep(0.2)

            if tournament_found:
                click_on_point(self.locs.tournament, pause=2)
                found, position = self.grabber.search(self.images.join)
                if found:
                    # A tournament is ready to be joined. First, we must travel the the base
                    # prestige screen, perform a prestige update, before joining the tournament.
                    self.logger.info("Tournament is available to join. Generating prestige instance before joining.")
                    click_on_point(MASTER_LOCS["screen_top"], pause=1)
                    if not self.goto_master(collapsed=False, top=False):
                        return False

                    click_on_point(MASTER_LOCS["prestige"], pause=3)
                    prestige_found = self.grabber.search(self.images.confirm_prestige, bool_only=True)
                    if prestige_found:
                        # Parsing the advanced start value that is present before a prestige takes place...
                        # This is used to improve stage parsing to not allow values < the advanced start value.
                        self.parse_advanced_start(self.stats.update_prestige(current_stage=self.current_stage, artifact=self.next_artifact_upgrade))
                        click_on_point(MASTER_LOCS["screen_top"], pause=1)

                    # Collapsing the master panel... Then attempting to join tournament.
                    self.goto_master()
                    click_on_point(self.locs.tournament, pause=2)
                    self.logger.info("Joining new tournament now...")
                    click_on_point(self.locs.join, pause=2)
                    click_on_point(self.locs.tournament_prestige, pause=35)
                    self.current_stage = self.ADVANCED_START

                    return True

                # Otherwise, maybe the tournament is over? Or still running.
                else:
                    collect_found, collect_position = self.grabber.search(self.images.collect_prize)
                    if collect_found:
                        self.logger.info("Tournament is over, attempting to collect reward now.")
                        click_on_point(self.locs.collect_prize, pause=2)
                        click_on_point(self.locs.game_middle, clicks=10, interval=0.5)
                        return False

    @not_in_transition
    def daily_rewards(self):
        """Collect any daily gifts if they're available."""
        self.logger.info("Checking if any daily rewards are currently available to collect.")
        if not self.goto_master():
            return False

        reward_found = self.grabber.search(self.images.daily_reward, bool_only=True)
        if reward_found:
            self.logger.info("Daily rewards are available, collecting now.")
            click_on_point(self.locs.open_rewards, pause=1)
            click_on_point(self.locs.collect_rewards, pause=1)
            click_on_point(self.locs.game_middle, 5, interval=0.5, pause=1)
            click_on_point(MASTER_LOCS["screen_top"], pause=1)

        return reward_found

    @not_in_transition
    def hatch_eggs(self):
        """Hatch any eggs if they're available."""
        if self.configuration.enable_egg_collection:
            self.logger.info("Checking if any eggs are available to be hatched in game.")
            if not self.goto_master():
                return False

            egg_found = self.grabber.search(self.images.hatch_egg, bool_only=True)
            if egg_found:
                self.logger.info("Egg(s) are available, collecting now.")
                click_on_point(self.locs.hatch_egg, pause=1)
                click_on_point(self.locs.game_middle, clicks=5, interval=0.5, pause=1)

            return egg_found

    @not_in_transition
    def clan_crate(self):
        """Check if a clan crate is currently available and collect it if one is."""
        if not self.goto_master():
            return False

        click_on_point(self.locs.clan_crate, pause=0.5)
        found, pos = self.grabber.search(self.images.okay)
        if found:
            self.logger.info("Clan crate was found, collecting now.")
            click_on_image(self.images.okay, pos, pause=1)

        return found

    @not_in_transition
    def daily_achievement_check(self, force=False):
        """Perform a check for any completed daily achievements, collecting them as long as any are present."""
        if self.configuration.enable_daily_achievements:
            now = timezone.now()
            if force or now > self.next_daily_achievement_check:
                self.logger.info("{force_or_initiate} daily achievement check now".format(force_or_initiate="Forcing" if force else "Beginning"))

                if not self.goto_master():
                    return False
                if not self.leave_boss():
                    return False

                # Open the achievements tab in game.
                click_on_point(MASTER_LOCS["achievements"], pause=2)

                # Are there any completed daily achievements?
                while self.grabber.search(self.images.daily_collect, bool_only=True):
                    found, pos = self.grabber.search(self.images.daily_collect)
                    if found:
                        # Collect the achievement reward here.
                        self.logger.info("Completed daily achievement found, collecting now.")
                        click_on_point(pos, pause=2)
                        click_on_point(GAME_LOCS["GAME_SCREEN"]["game_middle"], clicks=5, pause=1)
                        sleep(2)

                # Exiting achievements screen now.
                self.calculate_next_daily_achievement_check()
                click_on_point(MASTER_LOCS["screen_top"], clicks=3)

    @not_in_transition
    def clan_results_parse(self, force=False):
        """
        If the time threshold has been reached and clan result parsing is enabled, initiate the process
        in game to grab and parse out the information from the most recent results data taken from the current
        in game guild.

        A clan results parse will take the following steps:

            - Determine the name and id of the users current clan, if no clan is available or the name and id
              can not be successfully parsed, the function will exit early.

            - Grab the most recent "results" CSV data and parse it into some readable data points.

            - If the results grabbed are a duplicate (This will happen if the interval between checks takes place
              multiple times before a different raid is completed).

            - A digested version of the CSV data is used as the primary key for our clan results.
        """
        if self.configuration.enable_clan_results_parse:
            if force or timezone.now() > self.next_clan_results_parse:
                self.logger.info("{force_or_initiate} clan results parsing now.".format(
                    force_or_initiate="Forcing" if force else "Beginning"))

                # The clan results parse should take place.
                if not self.no_panel():
                    return False
                if not self.leave_boss():
                    return False

                # Travel to the clan page and attempt to parse out some generic
                # information about the current users clan.
                if not self._open_clan():
                    return False

                # Is the user in a clan or not? If no clan is present,
                # exiting early and not attempting to parse.
                if not self.grabber.search(self.images.clan_info, bool_only=True):
                    self.logger.warning("It looks like no clan is available to parse, giving up...")

                # A clan is available, begin by opening the information panel
                # to retrieve some generic information about the clan.
                click_on_point(self.locs.clan_info, pause=2)

                self.logger.info("Attempting to parse out generic clan information now...")

                # The clan info panel is open and we can attempt to grab the name and code
                # of the users current clan.
                name, code = self.stats.clan_name_and_code()

                if not name:
                    self.logger.warning("Unable to parse clan name, giving up...")
                    return False
                if not code:
                    self.logger.warning("Unable to parse clan code, giving up...")

                # Getting or creating the initial clan objects. Updating the clan name
                # if it's changed since the last results parse, the code may not change.
                try:
                    clan = Clan.objects.get(code=code)
                except Clan.DoesNotExist:
                    clan = Clan.objects.create(code=code, name=name)

                if clan.name != name:
                    self.logger.info("Clan name: {orig_name} has changed to {new_name}".format(orig_name=clan.name, new_name=name))
                    clan.name = name
                    clan.save()

                self.logger.info("{clan} was parsed successfully.".format(clan=clan))

                # At this point, the clan has been grabbed, safe to leave the information
                # panel and begin the retrieval of the current raid results.
                click_on_point(self.locs.clan_info_close, pause=1)

                self.logger.info("attempting to parse out most recent raid results from clan...")

                click_on_point(self.locs.clan_results, pause=2)
                click_on_point(self.locs.clan_results_copy, pause=1)

                win32clipboard.OpenClipboard()
                results = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                if not results:
                    self.logger.warning("no clipboard data was retrieved, giving up...")
                    return False

                # Attempting to generate the raid result for logging purposes,
                # if the raid found already exists, we'll simply return a False
                # boolean to determine this and log some info.
                raid = RaidResult.objects.generate(clipboard=results, clan=clan)

                if not raid:
                    self.logger.warning("The parsed raid results already exist and likely haven't changed since the last parse.")
                else:
                    self.logger.info("Successfully parsed and created a new raid result instance.")
                    self.logger.info("RaidResult: {raid}".format(raid=raid))

                self.calculate_next_clan_result_parse()

    @not_in_transition
    def collect_ad(self):
        """
        Collect ad if one is available on the screen.

        Note: This function does not require a max loop (FUNCTION_LOOP_TIMEOUT) since it only ever loops
              while the collect panel is on screen, this provides only two possible options.
        """
        while self.grabber.search(self.images.collect_ad, bool_only=True):
            if self.configuration.enable_premium_ad_collect:
                self.logger.info("Collecting premium ad now.")
                click_on_point(self.locs.collect_ad, pause=1, offset=1)
                self.stats.statistics.bot_statistics.premium_ads += 1
                self.stats.statistics.bot_statistics.save()
            else:
                self.logger.info("Declining premium ad now.")
                click_on_point(self.locs.no_thanks, pause=1, offset=1)

    def collect_ad_no_transition(self):
        """Collect ad if one is available on the screen. No transition wrapper is included here."""
        while self.grabber.search(self.images.collect_ad, bool_only=True):
            if self.configuration.enable_premium_ad_collect:
                self.logger.info("Collecting premium ad now.")
                click_on_point(self.locs.collect_ad, pause=1, offset=1)
                self.stats.statistics.bot_statistics.premium_ads += 1
                self.stats.statistics.bot_statistics.save()
            else:
                self.logger.info("Declining premium ad now.")
                click_on_point(self.locs.no_thanks, pause=1, offset=1)

    @not_in_transition
    def fight_boss(self):
        """Ensure that the boss is being fought if it isn't already."""
        loops = 0
        while True:
            loops += 1
            if loops == BOSS_LOOP_TIMEOUT:
                self.logger.warning("Error occurred, exiting function early.")
                self.ERRORS += 1
                return False

            if self.grabber.search(self.images.fight_boss, bool_only=True):
                self.logger.info("Attempting to initiate boss fight in game. ({tries}/{max})".format(tries=loops, max=BOSS_LOOP_TIMEOUT))
                click_on_point(self.locs.fight_boss, pause=0.8)
            else:
                break

        return True

    @not_in_transition
    def leave_boss(self):
        """Ensure that there is no boss being fought (avoids transition)."""
        loops = 0
        while True:
            loops += 1
            if loops == BOSS_LOOP_TIMEOUT:
                self.logger.warning("Error occurred, exiting function early.")
                self.ERRORS += 1
                return False

            if not self.grabber.search(self.images.fight_boss, bool_only=True):
                self.logger.info("Attempting to leave active boss fight in game. ({tries}/{max})".format(tries=loops, max=BOSS_LOOP_TIMEOUT))
                click_on_point(self.locs.fight_boss, pause=0.8)
            else:
                break

        # Sleeping for a bit after leaving boss fight in case some sort of
        # transition takes places directly after.
        sleep(3)
        return True

    @not_in_transition
    def tap(self):
        """Perform simple screen tap over entire game area."""
        if self.configuration.enable_tapping:
            self.logger.info("Tapping...")
            taps = 0
            for point in self.locs.fairies_map:
                taps += 1
                if taps == 5:
                    # Check for an ad as the tapping process occurs. Click and return early if one is available.
                    if self.grabber.search(self.images.collect_ad, bool_only=True):
                        self.collect_ad_no_transition()
                        return

                    # Reset taps counter.
                    taps = 0
                click_on_point(point)

            # If no transition state was found during clicks, wait a couple of seconds in case a fairy was
            # clicked just as the tapping ended.
            sleep(2)

    @not_in_transition
    def activate_skills(self, force=False):
        """Activate any skills off of cooldown, and determine if waiting for longest cd to be done."""
        if self.configuration.enable_skills:
            if not self.goto_master():
                return False

            # Datetime to determine skill intervals.
            now = timezone.now()
            skills = [s for s in self.skill_order if s[0] != 0]
            next_key = "next_"

            if self.configuration.force_enabled_skills_wait and not force:
                attr = getattr(self, next_key + skills[0][1])
                if not now > attr:
                    self.logger.info("Skills will only be activated once {key} is ready.".format(key=skills[0][1]))
                    self.logger.info("{key} will be ready in {time}.".format(key=skills[0][1], time=strfdelta(attr - now)))
                    return

            # If this point is reached, ensure no panel is currently active, and begin skill activation.
            if not self.no_panel():
                return False

            self.logger.info("Activating skills in game now.")
            for skill in skills:
                self.logger.info("Activating {skill} now.".format(skill=skill[1]))
                click_on_point(getattr(self.locs, skill[1]), pause=0.2)

            # Recalculate all skill execution times.
            self.calculate_skill_execution()
            return True

    @not_in_transition
    def _goto_panel(self, panel, icon, top_find, bottom_find, collapsed=True, top=True):
        """
        Goto a specific panel, panel represents the key of this panel, also used when determining what panel
        to click on initially.

        Icon represents the image in game that represents a panel being open. This image is searched
        for initially before attempting to move to the top or bottom of the specified panel.

        NOTE: This function will return a boolean to determine if the panel was reached successfully. This can be
              used to exit out of actions or other pieces of bot functionality early if something has gone wrong.
        """
        self.logger.debug("attempting to travel to the {collapse_expand} {top_bot} of {panel} panel".format(collapse_expand="collapsed" if collapsed else "expanded", top_bot="top" if top else "bottom", panel=panel))

        loops = 0
        while not self.grabber.search(icon, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("Error occurred while travelling to {panel} panel, exiting function early.".format(panel=panel))
                self.ERRORS += 1
                return False

            click_on_point(getattr(self.locs, panel), pause=1)

        # At this point, the panel should at least be opened.
        find = top_find if top or bottom_find is None else bottom_find

        # Trying to travel to the top or bottom of the specified panel, trying a set number of times
        # before giving up and breaking out of loop.
        loops = 0
        end_drag = self.locs.scroll_top_end if top else self.locs.scroll_bottom_end
        while not self.grabber.search(find, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("Error occurred while travelling to {panel} panel, exiting function early.".format(panel=panel))
                self.ERRORS += 1
                return False

            # Manually wrap drag_mouse function in the not_in_transition call, ensure that
            # un-necessary mouse drags are not performed.
            drag_mouse(self.locs.scroll_start, end_drag, pause=1)

        # The shop panel may not be expanded/collapsed. Skip when travelling to shop panel.
        if panel != "shop":
            # Ensure the panel is expanded/collapsed appropriately.
            loops = 0
            if collapsed:
                while not self.grabber.search(self.images.expand_panel, bool_only=True):
                    loops += 1
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("Unable to collapse panel: {panel}, exiting function early.".format(panel=panel))
                        self.ERRORS += 1
                        return False
                    click_on_point(self.locs.expand_collapse_top, pause=1, offset=1)
            else:
                while not self.grabber.search(self.images.collapse_panel, bool_only=True):
                    loops += 1
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("Unable to expand panel: {panel}, exiting function early.".format(panel=panel))
                        self.ERRORS += 1
                        return False
                    click_on_point(self.locs.expand_collapse_bottom, pause=1, offset=1)

        # Reaching this point represents a successful panel travel to.
        return True

    def goto_master(self, collapsed=True, top=True):
        """Instruct the bot to travel to the sword master panel."""
        return self._goto_panel("master", self.images.master_active, self.images.raid_cards, self.images.prestige, collapsed=collapsed, top=top)

    def goto_heroes(self, collapsed=True, top=True):
        """Instruct the bot to travel to the heroes panel."""
        return self._goto_panel("heroes", self.images.heroes_active, self.images.masteries, self.images.maya_muerta, collapsed=collapsed, top=top)

    def goto_equipment(self, collapsed=True, top=True):
        """Instruct the bot to travel to the heroes panel."""
        return self._goto_panel("equipment", self.images.equipment_active, self.images.crafting, None, collapsed=collapsed, top=top)

    def goto_pets(self, collapsed=True, top=True):
        """Instruct the bot to travel to the pets panel."""
        return self._goto_panel("pets", self.images.pets_active, self.images.next_egg, None, collapsed=collapsed, top=top)

    def goto_artifacts(self, collapsed=True, top=True):
        """Instruct the bot to travel to the artifacts panel."""
        return self._goto_panel("artifacts", self.images.artifacts_active, self.images.salvaged, None, collapsed=collapsed, top=top)

    def goto_shop(self, collapsed=False, top=True):
        """Instruct the bot to travel to the shop panel."""
        return self._goto_panel("shop", self.images.shop_active, self.images.shop_keeper, None, collapsed=collapsed, top=top)

    @not_in_transition
    def no_panel(self):
        """Instruct the bot to make sure no panels are currently open."""
        loops = 0
        while self.grabber.search(self.images.exit_panel, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("Error occurred while attempting to close all panels, exiting early.")
                self.ERRORS += 1
                return False

            click_on_point(self.locs.close_bottom, offset=2)
            if not self.grabber.search(self.images.exit_panel, bool_only=True):
                break

            click_on_point(self.locs.close_top, offset=2)
            if not self.grabber.search(self.images.exit_panel, bool_only=True):
                break

        return True

    @not_in_transition
    def _open_clan(self):
        """Open the clan panel in game."""
        self.logger.info("attempting to open the clan panel in game.")

        loops = 0
        while not self.grabber.search(self.images.clan, bool_only=True):
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.info("Unable to open clan panel, giving up.")
                return False

            loops += 1
            click_on_point(self.locs.clan)
            sleep(3)

        return True

    def soft_shutdown(self):
        """Perform a soft shutdown of the bot, taking care of any cleanup or related tasks."""
        self.logger.info("Beginning soft shutdown now.")
        self.update_stats(force=True)

    def pause(self):
        """Execute a pause for this Bot."""
        # Modify current BotInstance to be set to a PAUSED state.
        self.PAUSE = True
        BotInstance.objects.grab().pause()

    def resume(self):
        """Execute a resume for this Bot."""
        # Modify the current BotInstance to be set to a STARTED state.
        self.PAUSE = False
        BotInstance.objects.grab().resume()

    def terminate(self):
        """Execute a termination of this Bot instance."""
        self.TERMINATE = True

    def soft_terminate(self):
        """Execute a soft shutdown/termination of this Bot instance."""
        self.soft_shutdown()
        self.TERMINATE = True

    def setup_shortcuts(self):
        """Setup the keypress shortcut listener."""
        self.logger.info("Initiating Keyboard (Shortcut) Listener...")
        # Attach the ShortcutListener callback function that is called whenever a key is pressed.
        listener = ShortcutListener(logger=self.logger, cooldown=2)

        keyboard.on_press(callback=listener.on_press)
        keyboard.on_release(callback=listener.on_release)

    def run(self):
        """
        A run encapsulates the entire bot runtime process into a single function that conditionally
        checks for different things that are currently happening in the game, then launches different
        automated action within the emulator.
        """
        try:
            self.setup_shortcuts()
            self.goto_master()
            if self.configuration.activate_skills_on_start:
                self.activate_skills(force=True)
            if self.configuration.run_actions_on_start:
                self.actions(force=True)
            if self.configuration.update_stats_on_start:
                self.update_stats(force=True)
            if self.configuration.daily_achievements_check_on_start:
                self.daily_achievement_check(force=True)
            if self.configuration.parse_clan_results_on_start:
                self.clan_results_parse(force=True)

            # Update the initial bots artifacts information that is used when upgrading
            # artifacts in game. This is handled after stats have been updated.
            self.owned_artifacts = self.get_upgrade_artifacts()

            if self.configuration.upgrade_owned_artifacts:
                self.next_artifact_index = 0
                self.update_next_artifact_upgrade()

            # Setup main game loop variables.
            loop_funcs = [
                "goto_master", "fight_boss", "clan_crate", "tap", "collect_ad", "parse_current_stage", "prestige",
                "daily_achievement_check", "clan_results_parse", "actions", "activate_skills", "update_stats", "recover",
            ]

            # Generating an initial datetime that will be checked when the bot has been paused.
            # If this datetime is surpassed when the pause functionality is checked, a log will be sent.
            # Otherwise, we continue the loop normally.
            pause_log_dt = timezone.now() + datetime.timedelta(seconds=5)

            # Main game loop.
            while True:
                for func in loop_funcs:
                    # Any explicit functions can be executed after the main game loop has finished.
                    # The Queue handles the validation to ensure only available functions can be created...
                    for qfunc in Queue.objects.all().order_by("-created"):
                        if qfunc.function not in QUEUEABLE_FUNCTIONS:
                            self.logger.info("QueuedFunction: {func} encountered but this function does not exist on the Bot...".format(func=qfunc.function))
                            self.logger.info("Skipping queued function.")
                            qfunc.finish()
                            continue

                        self.current_function = "QUEUED: {func}".format(func=qfunc.function)

                        # Executing the function directly on the Bot. We can force the function if it
                        # requires it to be ran manually.
                        wait = wait_afterwards(
                            function=getattr(self, qfunc.function),
                            floor=self.configuration.post_action_min_wait_time,
                            ceiling=self.configuration.post_action_max_wait_time)

                        if qfunc.function in FORCEABLE_FUNCTIONS:
                            wait(force=True)
                        else:
                            wait()

                        qfunc.finish()

                    if self.TERMINATE:
                        self.logger.info("TERMINATE SIGNAL, EXITING.")
                        raise TerminationEncountered()
                    if self.PAUSE:
                        now = timezone.now()
                        if now > pause_log_dt:
                            pause_log_dt = now + datetime.timedelta(seconds=5)
                            self.logger.info("BOT IS PAUSED... WAITING FOR RESUME...")

                        # PAUSED. Continue loop forever unless resumed/stopped.
                        continue

                    self.current_function = func
                    wait_afterwards(getattr(self, func), floor=self.configuration.post_action_min_wait_time, ceiling=self.configuration.post_action_max_wait_time)()

        except TerminationEncountered:
            self.logger.info("MANUAL TERMINATION ENCOUNTERED: Terminating BotInstance...")
        except FailSafeException:
            self.logger.info("FAILSAFE TERMINATION ENCOUNTERED: Terminating BotInstance...")
        except Exception as exc:
            self.logger.critical("CRITICAL ERROR ENCOUNTERED: {exc}".format(exc=exc))
            self.logger.info("Terminating BotInstance...")
            if self.configuration.soft_shutdown_on_critical_error:
                self.logger.info("BotInstance Soft Shutdown is enabled on critical exception... Attempting to shutdown softly now...")
                self.soft_shutdown()

        # Cleaning up the BotInstance once a termination has been received.
        finally:
            self.stats.session.end = timezone.now()
            self.stats.session.save()
            self.instance.stop()
            Queue.flush()

            self.logger.info("=================================================================")
            self.logger.info("Session: {session} ended...".format(session=self.stats.session))
            self.logger.info("=================================================================")
