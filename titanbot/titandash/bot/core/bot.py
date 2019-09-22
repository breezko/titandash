"""
core.py

Main bot initialization and script startup should take place here. All actions and main bot loops
will be maintained from this location.
"""
from settings import STAGE_CAP, GAME_VERSION, BOT_VERSION, GIT_COMMIT

from django.utils import timezone

from titandash.models.queue import Queue
from titandash.models.clan import Clan, RaidResult

from titanauth.authentication.wrapper import AuthWrapper

from .maps import *
from .constants import (
    STAGE_PARSE_THRESHOLD, FUNCTION_LOOP_TIMEOUT, BOSS_LOOP_TIMEOUT,
    QUEUEABLE_FUNCTIONS, FORCEABLE_FUNCTIONS, PROPERTIES, BREAK_NEXT_PROPS
)
from .props import Props
from .grabber import Grabber
from .stats import Stats
from .wrap import Images, Locs, Colors
from .utilities import (
    click_on_point, click_on_image, drag_mouse, make_logger, strfdelta,
    strfnumber, sleep, send_raid_notification
)
from .decorators import not_in_transition, wait_afterwards, wrap_current_function
from .shortcuts import ShortcutListener

from pyautogui import easeOutQuad, FailSafeException, linear

import datetime
import random
import keyboard
import win32clipboard


class TerminationEncountered(Exception):
    pass


class Bot(object):
    """
    Main Bot Class.

    Initial setup is handled here, as well as some data setup for use during runtime.

    Statistics, Configurations and Logging is all setup here.
    """
    def __init__(self, configuration, window, instance, logger=None, start=False):
        """
        Initialize a new Bot. Setting up base variables as well as performing some bootstrapping
        to ensure authentication is handled before moving on.
        """
        self.TERMINATE = False
        self.PAUSE = False
        self.ERRORS = 0
        self.ADVANCED_START = None
        self.configuration = configuration
        self.window = window
        self.instance = instance
        self.instance.configuration = configuration
        self.instance.window = window.json()
        self.instance.errors = self.ERRORS

        # Initialize and setup our Props object which is used to handle BotInstance
        # realtime updates using our Django Channels sockets.
        self.props = Props(instance=self.instance, props=PROPERTIES)
        self.last_stage = None

        self.logger = logger if logger else make_logger(instance, self.configuration.logging_level, log_file=None)
        if not self.configuration.enable_logging:
            self.logger.disabled = True

        # Bot utilities.
        self.grabber = Grabber(window=self.window, logger=self.logger)
        self.stats = Stats(instance=self.instance, window=self.window, grabber=self.grabber, configuration=self.configuration, logger=self.logger)

        # Statistics handles Log instance creation... Set BotInstance now.
        self.instance.log = self.stats.session.log

        # Data containers.
        self.images = Images(IMAGES, self.logger)
        self.locs = Locs(GAME_LOCS, self.logger)
        self.colors = Colors(GAME_COLORS, self.logger)

        self.instance.start(session=self.stats.session)
        self.instance_string = "bot (v{version}) (v{game_version}){git} has been initialized".format(
            version=BOT_VERSION,
            game_version=GAME_VERSION,
            git=" [{commit}]".format(commit=GIT_COMMIT[:10]) if GIT_COMMIT else " "
        )

        self.logger.info("==========================================================================================")
        self.logger.info(self.instance_string)
        self.logger.info("{session}".format(session=self.stats.session))
        self.logger.info("==========================================================================================")

        # Set authentication reference to an online state.
        AuthWrapper().online()

        # Create a list of the functions called in there proper order
        # when actions are performed by the bot.
        self.action_order = self.order_actions()
        self.skill_order = self.order_skill_intervals()

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
        self.calculate_next_raid_notifications_check()
        self.calculate_next_clan_result_parse()
        self.calculate_next_break()

        if start:
            self.run()

    def click(self, point, clicks=1, interval=0.0, button="left", pause=0.0, offset=5):
        """
        Local click method for use with the bot, ensuring we pass the window being used into the click function.
        """
        click_on_point(point=point, window=self.window, clicks=clicks, interval=interval, button=button, pause=pause, offset=offset)

    def drag(self, start, end, button="left", duration=0.3, pause=0.5, tween=linear, quick_stop=None):
        """
        Local drag method for use with the bot, ensuring we pass the window being used into the drag function.
        """
        drag_mouse(start=start, end=end, window=self.window, button=button, duration=duration, pause=pause, tween=tween, quick_stop=quick_stop)

    @wrap_current_function
    def get_upgrade_artifacts(self, testing=False):
        """
        Retrieve a list of all discovered/owned artifacts in game that will be iterated over
        and upgraded throughout runtime.

        The testing boolean is used to ignore the owned filter so all artifacts will be grabbed
        and can be tested thoroughly.
        """
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
                self.logger.debug("{artifact} will be upgraded".format(artifact=artifact))
                continue

        if len(lst) == 0:
            self.logger.error("no owned artifacts were found... parsed artifacts must be present before starting a session.")
            self.logger.info("attempting to force artifacts parse now...")
            self.parse_artifacts()
            lst = self.get_upgrade_artifacts()

            if len(lst) == 0:
                self.logger.error("no artifacts were parsed... disabling artifact purchase for this session.")
                self.configuration.enable_artifact_purchase = False

        if self.configuration.shuffle_artifacts:
            random.shuffle(lst)

        return lst

    @wrap_current_function
    def update_next_artifact_upgrade(self):
        """
        Update the next artifact to be upgraded to the next one in the list.
        """
        if self.next_artifact_index == len(self.owned_artifacts):
            self.next_artifact_index = 0

        self.next_artifact_upgrade = self.owned_artifacts[self.next_artifact_index]
        self.next_artifact_index += 1

        self.instance.next_artifact_upgrade = self.next_artifact_upgrade
        self.instance.save()

        self.logger.info("next artifact upgrade: {artifact}".format(artifact=self.next_artifact_upgrade))

    @wrap_current_function
    def parse_advanced_start(self, stage_text):
        """
        Attempt to parse out the advanced start stage value into a valid integer.
        """
        try:
            stage = int(stage_text)
            self.logger.info("advanced start stage: {stage_text} was successfully coerced into an integer: {stage}".format(
                stage_text=stage_text, stage=strfnumber(stage)))

            if stage > STAGE_CAP:
                self.logger.info("stage: {stage} is greater then {stage_cap}, resetting advanced start now.".format(
                    stage=strfnumber(stage), stage_cap=STAGE_CAP))
                self.ADVANCED_START = None
                return

            self.logger.info("current advanced start in game was successfully parsed: {stage}".format(stage=strfnumber(stage)))
            self.ADVANCED_START = stage

        except ValueError:
            self.logger.warning("ocr check could not parse out a proper string from image, resetting advanced start value...")
            self.ADVANCED_START = None
        except TypeError:
            self.logger.warning("ocr check could not be coerced properly into an integer, resetting advanced start value...")
            self.logger.warning("text: {text}".format(text=stage_text))
            self.ADVANCED_START = None

    @wrap_current_function
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
            self.logger.info("stage {stage_text} was successfully coerced into an integer: {stage}.".format(
                stage_text=stage_parsed, stage=strfnumber(stage)))
            if stage > STAGE_CAP:
                self.logger.info("stage {stage} is greater then the stage cap: {stage_cap}, resetting stage variables.".format(
                    stage=strfnumber(stage), stage_cap=STAGE_CAP))
                return

            if self.ADVANCED_START:
                if stage < self.ADVANCED_START:
                    self.logger.info("stage: {stage} is less then the advanced start: {advanced_start}, leaving current stage unchanged.".format(
                        stage=strfnumber(stage), advanced_start=self.ADVANCED_START))
                    return

            # Is the stage potentially way greater than the last check? Could mean the parse failed.
            if isinstance(self.last_stage, int):
                diff = stage - self.last_stage
                if diff > STAGE_PARSE_THRESHOLD:
                    self.logger.info(
                        "difference between current stage and last stage passes the stage change threshold: "
                        "{stage_thresh} ({stage} - {last_stage} = {diff}), resetting stage variables...".format(
                            stage_thresh=STAGE_PARSE_THRESHOLD, stage=strfnumber(stage), last_stage=strfnumber(self.last_stage), diff=strfnumber(diff)))

                    self.last_stage, self.props.current_stage = None, None
                    return

            self.logger.info("current stage in game was successfully parsed: {stage}".format(stage=strfnumber(stage)))
            self.last_stage = self.props.current_stage
            self.logger.info("last stage has been set to the previous current stage in game: {last_stage}".format(last_stage=strfnumber(self.last_stage)))
            self.props.current_stage = stage

        # ValueError when the parsed stage isn't able to be coerced.
        except ValueError:
            self.logger.error("ocr check could not parse out a proper string from image, leaving stage variables as they were before...")
            self.logger.info("current stage: {current}".format(current=strfnumber(self.props.current_stage)))
            self.logger.info("last stage: {last}".format(last=strfnumber(self.last_stage)))
            self.last_stage, self.props.current_stage = None, None

    @wrap_current_function
    def order_actions(self):
        """
        Determine order of in game actions. Mapped to their respective functions.
        """
        sort = sorted([
            (self.configuration.order_level_heroes, self.level_heroes, "level_heroes"),
            (self.configuration.order_level_master, self.level_master, "level_master"),
            (self.configuration.order_level_skills, self.level_skills, "level_skills"),
        ], key=lambda x: x[0])

        self.logger.info("actions in game have been ordered successfully...")
        for action in sort:
            self.logger.info("{order} : {action_key}.".format(order=action[0], action_key=action[2]))

        return sort

    @wrap_current_function
    def order_skill_intervals(self):
        """
        Determine order of skills with intervals, first index will be the longest interval.
        """
        sort = sorted([
            (self.configuration.interval_heavenly_strike, "heavenly_strike"),
            (self.configuration.interval_deadly_strike, "deadly_strike"),
            (self.configuration.interval_fire_sword, "hand_of_midas"),
            (self.configuration.interval_fire_sword, "fire_sword"),
            (self.configuration.interval_shadow_clone, "war_cry"),
            (self.configuration.interval_shadow_clone, "shadow_clone"),
        ], key=lambda x: x[0], reverse=True)

        self.logger.info("skill intervals have been ordered successfully.")
        for index, skill in enumerate(sort, start=1):
            if skill[0] != 0:
                self.logger.info("{index}: {key} ({interval})".format(index=index, key=skill[1], interval=skill[0]))

        return sort

    @wrap_current_function
    @not_in_transition
    def inactive_skills(self):
        """
        Create a list of all skills that are currently inactive.
        """
        inactive = []
        for key, region in MASTER_COORDS["skills"].items():
            if self.grabber.search(self.images.cancel_active_skill, region, bool_only=True):
                continue
            inactive.append(key)

        for key in inactive:
            self.logger.info("{key} is not currently activated.".format(key=key))

        return inactive

    @wrap_current_function
    @not_in_transition
    def not_maxed(self, inactive):
        """
        Given a list of inactive skill keys, determine which ones are not maxed.
        """
        not_maxed = []
        for key, region in {k: r for k, r in MASTER_COORDS["skills"].items() if k in inactive}.items():
            if self.grabber.search(self.images.skill_max_level, region, bool_only=True):
                continue
            not_maxed.append(key)

        for key in not_maxed:
            self.logger.info("{key} is not currently max level.".format(key=key))

        return not_maxed

    @wrap_current_function
    def calculate_skill_execution(self):
        """
        Calculate the datetimes that are attached to each skill in game and when they should be activated.
        """
        now = timezone.now()
        for key in SKILLS:
            interval_key = "interval_{0}".format(key)
            next_key = "next_{0}".format(key)
            interval = getattr(self.configuration, interval_key, 0)
            if interval != 0:
                dt = now + datetime.timedelta(seconds=interval)
                setattr(self.props, next_key, dt)
                self.logger.info("{skill} will be activated in {time}.".format(skill=key, time=strfdelta(dt - now)))
            else:
                self.logger.info("{skill} has interval set to zero, will not be activated.".format(skill=key))

    @wrap_current_function
    def calculate_next_prestige(self):
        """
        Calculate when the next timed prestige will take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.prestige_x_minutes * 60)
        self.props.next_prestige = dt
        self.logger.info("the next timed prestige will take place in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_recovery_reset(self):
        """
        Calculate when the next recovery reset will take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.recovery_check_interval_minutes * 60)
        self.props.next_recovery_reset = dt
        self.logger.info("the next recovery reset will take place in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
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
                self.logger.info("forcing an in game recovery now and attempting to restart the game.")
            else:
                self.logger.info("{amount} errors have occurred before a reset, attempting to restart the game now...".format(amount=self.ERRORS))

            sleep(3)
            # Restart the emulator and wait for a while for it to boot up...
            self.restart_emulator()
            self.open_game()

            self.calculate_next_recovery_reset()
            return

        # Otherwise, determine if the error counter should be reset at this point.
        # To ensure an un-necessary recovery doesn't take place.
        else:
            now = timezone.now()
            if now > self.props.next_recovery_reset:
                self.logger.info("{amount}/{needed} errors occurred before reset, recovery will not take place.".format(amount=self.ERRORS, needed=self.configuration.recovery_allowed_failures))
                self.logger.info("resetting error count now...")
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
            self.logger.info("timed prestige is enabled, and should take place in {time}".format(time=strfdelta(self.props.next_prestige - now)))

            # Is the hard time limit set? If it is, perform prestige no matter what,
            # otherwise, look at the current stage conditionals present and prestige
            # off of those instead.
            if now > self.props.next_prestige:
                self.logger.debug("timed prestige will happen now.")
                return True

        # Current stage must not be None, using time gate before this check. stage == None is only possible when
        # OCR checks are failing, this can happen when a stage change happens as the check takes place, causing
        # the image recognition to fail. OR if the parsed text doesn't pass the validation checks when parse is
        # malformed.
        if self.props.current_stage is None:
            self.logger.info("current stage is currently none, no stage conditionals can be checked...")
            return False

        # Any other conditionals will be using the current stage attribute of the bot.
        elif self.configuration.prestige_at_stage != 0:
            self.logger.info("prestige at specific stage: {current}/{needed}.".format(current=strfnumber(self.props.current_stage), needed=strfnumber(self.configuration.PRESTIGE_AT_STAGE)))
            if self.props.current_stage >= self.configuration.prestige_at_stage:
                self.logger.info("prestige stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        # These conditionals are dependant on the highest stage reached taken
        # from the bot's current game statistics.
        if self.configuration.prestige_at_max_stage:
            self.logger.info("prestige at max stage: {current}/{needed}.".format(current=strfnumber(self.props.current_stage), needed=strfnumber(self.stats.highest_stage)))
            if self.props.current_stage >= self.stats.highest_stage:
                self.logger.info("max stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        elif self.configuration.prestige_at_max_stage_percent != 0:
            percent = float(self.configuration.prestige_at_max_stage_percent) / 100
            threshold = int(self.stats.highest_stage * percent)
            self.logger.info("prestige at max stage percent ({percent}): {current}/{needed}".format(percent=percent, current=strfnumber(self.props.current_stage), needed=strfnumber(threshold)))
            if self.props.current_stage >= threshold:
                self.logger.info("percent of max stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        # Otherwise, only a time limit has been set for a prestige and it wasn't reached.
        return False

    @wrap_current_function
    def calculate_next_action_run(self):
        """
        Calculate when the next set of actions will be ran.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.run_actions_every_x_seconds)
        self.props.next_action_run = dt
        self.logger.info("enabled actions in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_stats_update(self):
        """
        Calculate when the next stats update should take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.update_stats_every_x_minutes * 60)
        self.props.next_stats_update = dt
        self.logger.info("in game statistics update in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_daily_achievement_check(self):
        """
        Calculate when the next daily achievement check should take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(hours=self.configuration.daily_achievements_check_every_x_hours)
        self.props.next_daily_achievement_check = dt
        self.logger.info("daily achievement check in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_raid_notifications_check(self):
        """
        Calculate when the next raid notifications check should take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(minutes=self.configuration.raid_notifications_check_every_x_minutes)
        self.props.next_raid_notifications_check = dt
        self.logger.info("raid notifications check will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_clan_result_parse(self):
        """
        Calculate when the next clan result parse should take place.
        """
        if self.configuration.enable_clan_results_parse:
            now = timezone.now()
            dt = now + datetime.timedelta(minutes=self.configuration.parse_clan_results_every_x_minutes)
            self.props.next_clan_results_parse = dt
            self.logger.info("clan results parse in game will be initiated in {time}".format(time=strfdelta(dt - now)))
        else:
            # If result parsing is disabled, No datetime is configured and will be ignored.
            self.props.next_clan_results_parse = None

    @wrap_current_function
    def calculate_next_break(self):
        """
        Calculate when the next break will take place in game.
        """
        if self.configuration.enable_breaks:
            now = timezone.now()

            # Calculating when the next break will begin.
            jitter = random.randint(-self.configuration.breaks_jitter, self.configuration.breaks_jitter)
            jitter = self.configuration.breaks_minutes_required + jitter

            next_break_dt = now + datetime.timedelta(minutes=jitter)

            # Calculate the datetime to determine when the bot will be resumed after a break takes place.
            resume_jitter = random.randint(self.configuration.breaks_minutes_min, self.configuration.breaks_minutes_max)
            next_break_res = next_break_dt + datetime.timedelta(minutes=resume_jitter + 10)

            self.props.next_break = next_break_dt
            self.props.resume_from_break = next_break_res

    @wrap_current_function
    @not_in_transition
    def level_heroes(self):
        """
        Perform all actions related to the levelling of all heroes in game.
        """
        if self.configuration.enable_heroes:
            self.logger.info("levelling heroes in game...")
            if not self.goto_heroes(collapsed=False):
                return False

            # A quick check can be performed to see if the top of the heroes panel contains
            # a hero that is already max level, if this is the case, it's safe to assume
            # that all heroes below have been maxed out. Instead of scrolling and levelling
            # all heroes, just level the top heroes.
            if self.grabber.search(self.images.max_level, bool_only=True):
                self.logger.info("a max levelled hero has been found! Only first set of heroes will be levelled.")
                for point in HEROES_LOCS["level_heroes"][::-1][1:9]:
                    self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                # Early exit as well.
                return

            # Always level the first 5 heroes in the list.
            self.logger.info("levelling the first five heroes available.")
            for point in HEROES_LOCS["level_heroes"][::-1][1:6]:
                self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

            # Travel to the bottom of the panel.
            for i in range(5):
                self.drag(start=self.locs.scroll_start, end=self.locs.scroll_bottom_end)

            drag_start = HEROES_LOCS["drag_heroes"]["start"]
            drag_end = HEROES_LOCS["drag_heroes"]["end"]

            # Begin level and scrolling process. An assumption is made that all heroes
            # are unlocked, meaning that some un-necessary scrolls may take place.
            self.logger.info("scrolling and levelling all heroes present.")
            for i in range(4):
                for point in HEROES_LOCS["level_heroes"]:
                    self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                # Skip the last drag since it's un-needed.
                if i != 3:
                    self.drag(start=drag_start, end=drag_end, duration=1, pause=1, tween=easeOutQuad, quick_stop=self.locs.scroll_quick_stop)

    @wrap_current_function
    @not_in_transition
    def level_master(self):
        """
        Perform all actions related to the levelling of the sword master in game.
        """
        if self.configuration.enable_master:
            self.logger.info("levelling the sword master {clicks} time(s)".format(clicks=self.configuration.master_level_intensity))
            if not self.goto_master(collapsed=False):
                return False

            self.click(point=MASTER_LOCS["master_level"], clicks=self.configuration.master_level_intensity)

    @wrap_current_function
    @not_in_transition
    def level_skills(self):
        """
        Perform all actions related to the levelling of skills in game.
        """
        if self.configuration.enable_skills:
            self.logger.info("levelling up inactive and un-maxed skills in game.")
            if not self.goto_master(collapsed=False):
                return False

            # Looping through each skill coord, clicking to level up.
            for skill in self.not_maxed(self.inactive_skills()):
                point = MASTER_LOCS["skills"].get(skill)

                # Should the bot upgrade the max amount of upgrades available for the current skill?
                if self.configuration.max_skill_if_possible:
                    # Retrieve the pixel location where the color should be the proper max level
                    # color once a single click takes place.
                    color_point = MASTER_LOCS["skill_level_max"].get(skill)
                    self.click(point=point, pause=1)

                    # Take a snapshot right after, and check for the point being the proper color.
                    self.grabber.snapshot()
                    if self.grabber.current.getpixel(color_point) == self.colors.WHITE:
                        self.logger.info("levelling max amount of available upgrades for skill: {skill}.".format(skill=skill))
                        self.click(point=color_point, pause=0.5)

                # Otherwise, just level up the skills normally using the intensity setting.
                else:
                    self.logger.info("levelling skill: {skill} {intensity} time(s).".format(skill=skill, intensity=self.configuration.skill_level_intensity))
                    self.click(point=MASTER_LOCS["skills"].get(skill), clicks=self.configuration.skill_level_intensity)

    @not_in_transition
    def actions(self, force=False):
        """
        Perform bot actions in game.
        """
        now = timezone.now()
        if force or now > self.props.next_action_run:
            self.logger.info("{force_or_initiate} in game actions now.".format(
                force_or_initiate="forcing" if force else "beginning"))
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

    @wrap_current_function
    @not_in_transition
    def update_stats(self, force=False):
        """
        Update the bot stats by travelling to the stats page in the heroes panel and performing OCR update.
        """
        if self.configuration.enable_stats:
            now = timezone.now()
            if force or now > self.props.next_stats_update:
                self.logger.info("{force_or_initiate} in game statistics update now.".format(
                    force_or_initiate="forcing" if force else "beginning"))

                # Leaving boss fight here so that a stage transition does not take place
                # in the middle of a stats update.
                if not self.leave_boss():
                    return False

                # Sleeping slightly before attempting to goto top of heroes panel so that new hero
                # levels doesn't cause the 'top' of the panel to disappear after travelling.
                sleep(3)
                if not self.goto_heroes():
                    return False

                # Ensure we are at the top of the stats screen while collapsed.
                while not self.grabber.search(self.images.stats, bool_only=True):
                    self.drag(start=self.locs.scroll_start, end=self.locs.scroll_top_end)
                # Ensure the stats panel has been opened before continuing.
                while not self.grabber.search(self.images.stats_title, bool_only=True):
                    self.click(point=HEROES_LOCS["stats_collapsed"], pause=1)

                # Scrolling to the bottom of the stats panel.
                sleep(2)
                for i in range(5):
                    self.drag(start=self.locs.scroll_start, end=self.locs.scroll_bottom_end)

                self.stats.update_ocr()
                self.stats.statistics.bot_statistics.updates += 1
                self.stats.statistics.bot_statistics.save()

                self.calculate_next_stats_update()
                self.click(point=MASTER_LOCS["screen_top"], clicks=3)

    @wrap_current_function
    @not_in_transition
    def prestige(self, force=False):
        """
        Perform a prestige in game.
        """
        if self.configuration.enable_auto_prestige:
            if self.should_prestige() or force:
                self.logger.info("{begin_force} prestige process in game now.".format(
                    begin_force="beginning" if not force else "forcing"))
                tournament = self.check_tournament()

                # If tournament==True, then a tournament was available to join (which means we prestiged, exit early).
                if tournament:
                    return False
                if not self.goto_master(collapsed=False, top=False):
                    return False

                # Click on the prestige button, and check for the prompt confirmation being present. Sleeping
                # slightly here to ensure that connections issues do not cause the prestige to be misfire.
                self.click(point=MASTER_LOCS["prestige"], pause=3)
                prestige_found, prestige_position = self.grabber.search(self.images.confirm_prestige)
                if prestige_found:
                    # Parsing the advanced start value that is present before a prestige takes place...
                    # This is used to improve stage parsing to not allow values < the advanced start value.
                    prestige, advanced_start = self.stats.update_prestige(artifact=self.next_artifact_upgrade, current_stage=self.props.current_stage)
                    self.props.last_prestige = prestige
                    self.parse_advanced_start(advanced_start)

                    self.click(point=MASTER_LOCS["prestige_confirm"], pause=1)
                    # Waiting for a while after prestiging, this reduces the chance
                    # of a game crash taking place due to many clicks while game is resetting.
                    self.click(point=MASTER_LOCS["prestige_final"], pause=35)

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
                    if self.props.current_stage and self.stats.highest_stage:
                            if self.props.current_stage > self.stats.highest_stage:
                                self.logger.info("current stage is greater than your previous max stage {max}, forcing a stats update to reflect new max stage.".format(
                                    max=self.stats.highest_stage))
                                self.update_stats(force=True)

                    self.props.current_stage = self.ADVANCED_START

                    # Additional checks can take place during a prestige.
                    self.artifacts()
                    self.daily_rewards()
                    self.hatch_eggs()

    @wrap_current_function
    @not_in_transition
    def parse_artifacts(self):
        """
        Begin the process to parse owned artifacts from in game.
        """
        self.logger.info("beginning artifact parsing process.")
        if not self.leave_boss():
            return False
        if not self.goto_artifacts(collapsed=False):
            return False

        # We are at the artifacts panel collapsed at this point... Begin parsing.
        self.stats.parse_artifacts()

    @wrap_current_function
    @not_in_transition
    def artifacts(self):
        """
        Determine whether or not any artifacts should be purchased, and purchase them.
        """
        if self.configuration.enable_artifact_purchase:
            self.logger.info("beginning artifact purchase process.")
            if not self.goto_artifacts(collapsed=False):
                return False

            if self.configuration.upgrade_owned_artifacts:
                artifact = self.next_artifact_upgrade
                self.update_next_artifact_upgrade()

            # Fallback to the users first artifact. This shouldn't happen, better safe than sorry.
            else:
                artifact = self.owned_artifacts[0]

            self.logger.info("attempting to upgrade {artifact} now.".format(artifact=artifact))

            # Make sure that the proper spend max multiplier is used to fully upgrade an artifact.
            # 1.) Ensure that the percentage (%) multiplier is selected.
            loops = 0
            while not self.grabber.search(self.images.percent_on, bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("unable to set the artifact buy multiplier to use percentage, skipping...")
                    self.ERRORS += 1
                    return False

                self.click(point=ARTIFACTS_LOCS["percent_toggle"], pause=0.5)

            # 2.) Ensure that the SPEND Max multiplier is selected.
            loops = 0
            while not self.grabber.search(self.images.spend_max, bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("unable to set the spend multiplier to spend max... skipping.")
                    self.ERRORS += 1
                    return False

                self.click(point=ARTIFACTS_LOCS["buy_multiplier"], pause=0.5)
                self.click(point=ARTIFACTS_LOCS["buy_max"], pause=0.5)

            # Looking for the artifact to upgrade here, dragging until it is finally found.
            loops = 0
            while not self.grabber.search(ARTIFACT_MAP.get(artifact), bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("artifact: {artifact} couldn't be found on screen... skipping.".format(artifact=artifact))
                    self.ERRORS += 1
                    return False

                self.drag(start=self.locs.scroll_start, end=self.locs.scroll_bottom_end, quick_stop=self.locs.scroll_quick_stop)

            # Making it here means the artifact in question has been found.
            found, position = self.grabber.search(ARTIFACT_MAP.get(artifact))
            new_x = position[0] + ARTIFACTS_LOCS["artifact_push"]["x"] + self.window.x
            new_y = position[1] + ARTIFACTS_LOCS["artifact_push"]["y"] + self.window.y

            # Currently just upgrading the artifact to it's max level. Future updates may include the ability
            # to determine how much to upgrade an artifact by.
            self.click(point=(new_x, new_y), pause=1)

    @not_in_transition
    def check_tournament(self):
        """
        Check that a tournament is available/active. Tournament will be joined if a new possible.
        """
        if self.configuration.enable_tournaments:
            self.logger.info("checking for tournament ready to join or in progress.")
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
                self.click(point=self.locs.tournament, pause=2)
                found, position = self.grabber.search(self.images.join)
                if found:
                    # A tournament is ready to be joined. First, we must travel the the base
                    # prestige screen, perform a prestige update, before joining the tournament.
                    self.logger.info("tournament is available to join. generating prestige instance before joining.")
                    self.click(point=MASTER_LOCS["screen_top"], pause=1)
                    if not self.goto_master(collapsed=False, top=False):
                        return False

                    self.click(point=MASTER_LOCS["prestige"], pause=3)
                    prestige_found = self.grabber.search(self.images.confirm_prestige, bool_only=True)
                    if prestige_found:
                        # Parsing the advanced start value that is present before a prestige takes place...
                        # This is used to improve stage parsing to not allow values < the advanced start value.
                        self.parse_advanced_start(self.stats.update_prestige(current_stage=self.props.current_stage, artifact=self.next_artifact_upgrade))
                        self.click(point=MASTER_LOCS["screen_top"], pause=1)

                    # Collapsing the master panel... Then attempting to join tournament.
                    self.goto_master()
                    self.click(point=self.locs.tournament, pause=2)
                    self.logger.info("joining new tournament now...")
                    self.click(point=self.locs.join, pause=2)
                    self.click(point=self.locs.tournament_prestige, pause=35)
                    self.props.current_stage = self.ADVANCED_START

                    return True

                # Otherwise, maybe the tournament is over? Or still running.
                else:
                    collect_found, collect_position = self.grabber.search(self.images.collect_prize)
                    if collect_found:
                        self.logger.info("tournament is over, attempting to collect reward now.")
                        self.click(point=self.locs.collect_prize, pause=2)
                        self.click(point=self.locs.game_middle, clicks=10, interval=0.5)
                        return False

    @wrap_current_function
    @not_in_transition
    def daily_rewards(self):
        """
        Collect any daily gifts if they're available.
        """
        self.logger.info("checking if any daily rewards are currently available to collect.")
        if not self.goto_master():
            return False

        reward_found = self.grabber.search(self.images.daily_reward, bool_only=True)
        if reward_found:
            self.logger.info("daily rewards are available, collecting!")
            self.click(point=self.locs.open_rewards, pause=1)
            self.click(point=self.locs.collect_rewards, pause=1)
            self.click(point=self.locs.game_middle, clicks=5, interval=0.5, pause=1)
            self.click(point=MASTER_LOCS["screen_top"], pause=1)

        return reward_found

    @wrap_current_function
    @not_in_transition
    def hatch_eggs(self):
        """
        Hatch any eggs if they're available.
        """
        if self.configuration.enable_egg_collection:
            self.logger.info("checking if any eggs are available to be hatched in game.")
            if not self.goto_master():
                return False

            egg_found = self.grabber.search(self.images.hatch_egg, bool_only=True)
            if egg_found:
                self.logger.info("egg(s) are available, collecting!")
                self.click(point=self.locs.hatch_egg, pause=1)
                self.click(point=self.locs.game_middle, clicks=5, interval=0.5, pause=1)

            return egg_found

    @wrap_current_function
    @not_in_transition
    def clan_crate(self):
        """
        Check if a clan crate is currently available and collect it if one is.
        """
        if not self.goto_master():
            return False

        self.click(point=self.locs.clan_crate, pause=0.5)
        found, pos = self.grabber.search(self.images.okay)
        if found:
            self.logger.info("clan crate is available, collecting!")
            click_on_image(self.images.okay, pos, pause=1)

        return found

    @wrap_current_function
    @not_in_transition
    def breaks(self, force=False):
        """
        Check to see if a break should take place, if a break should take place, the emulator will
        be restarted and the bot will wait until the resume time has been reached, then the game
        will be opened once again and the bot will resume its functionality. A resume will also
        cause all calculable variables to be recalculated.
        """
        if self.configuration.enable_breaks:
            assert self.props.next_break and self.props.resume_from_break
            now = timezone.now()
            if force or now > self.props.next_break:
                # A break can now take place...
                # Begin by completely restarting the emulator.
                # After that has been completed, we will initiate a while loop
                # that keeps the bot here until the break has ended.
                if not self.restart_emulator():
                    return False

                time_break = self.props.next_break - now
                time_resume = self.props.resume_from_break - now
                delta = time_resume - time_break

                # Forcing a break should modify our next break values to now plus whatever
                # the most recent break was calculated as.
                if force:
                    self.props.next_break = now
                    self.props.resume_from_break = now + delta

                # Modify all next attributes to take place after their normal calculated
                # time with a bit of padding after a break ends.
                for prop in BREAK_NEXT_PROPS:
                    current = getattr(self.props, prop, None)
                    if current:
                        # Adding a bit of padding to next activation values.
                        new = current + delta + datetime.timedelta(seconds=30)
                        setattr(self.props, prop, new)

                break_log_dt = now + datetime.timedelta(seconds=60)
                self.logger.info("waiting for break to end... ({break_end})".format(break_end=strfdelta(self.props.resume_from_break - now)))
                while True:
                    now = timezone.now()
                    if now > self.props.resume_from_break:
                        self.logger.info("break has ended... opening game now.")
                        if not self.open_game():
                            return False

                        self.calculate_next_break()
                        return True

                    if now > break_log_dt:
                        break_log_dt = now + datetime.timedelta(seconds=60)
                        self.logger.info("waiting for break to end... ({break_end})".format(break_end=strfdelta(self.props.resume_from_break - now)))

                    sleep(1)

    @wrap_current_function
    @not_in_transition
    def daily_achievement_check(self, force=False):
        """
        Perform a check for any completed daily achievements, collecting them as long as any are present.
        """
        if self.configuration.enable_daily_achievements:
            now = timezone.now()
            if force or now > self.props.next_daily_achievement_check:
                self.logger.info("{force_or_initiate} daily achievement check now".format(
                    force_or_initiate="forcing" if force else "beginning"))

                if not self.goto_master():
                    return False
                if not self.leave_boss():
                    return False

                # Open the achievements tab in game.
                self.click(point=MASTER_LOCS["achievements"], pause=2)

                # Are there any completed daily achievements?
                while self.grabber.search(self.images.daily_collect, bool_only=True):
                    found, pos = self.grabber.search(self.images.daily_collect)
                    if found:
                        # Collect the achievement reward here.
                        self.logger.info("completed daily achievement found, collecting now.")
                        click_on_image(image=self.images.daily_collect, pos=pos)

                # Check for the single ad watching daily achievement.
                found, pos = self.grabber.search(self.images.daily_watch)
                if found:
                    self.logger.info("watching daily achievement ad.")
                    click_on_image(image=self.images.daily_watch, pos=pos)
                    sleep(30)

                    # Ad likely finished at this point, attempt to close the ad now by using the
                    # back button within the emulator.
                    self.logger.info("attempting to close watched ad.")
                    self.click(self.locs.back_emulator, pause=3)

                    # Attempt to collect the ad.
                    found, pos = self.grabber.search(self.images.daily_collect)
                    if found:
                        click_on_image(image=self.images.daily_collect, pos=pos)

                # Exiting achievements screen now.
                self.calculate_next_daily_achievement_check()
                self.click(point=MASTER_LOCS["screen_top"], clicks=3)

    @wrap_current_function
    @not_in_transition
    def raid_notifications(self, force=False):
        """
        Perform all checks to see if a sms message will be sent to notify a user of an active raid.
        """
        if self.configuration.enable_raid_notifications:
            now = timezone.now()
            if force or now > self.props.next_raid_notifications_check:
                self.logger.info("{force_or_initiate} raid notifications check now".format(
                    force_or_initiate="forcing" if force else "beginning"))

                # Has an attack reset value already been parsed?
                if self.props.next_raid_attack_reset:
                    if self.props.next_raid_attack_reset > now:
                        self.logger.info("the next raid attack reset is still in the future, no notification will be sent.")
                        self.calculate_next_raid_notifications_check()
                        return False

                # Opening up the clan raid panel and checking if the fight button is available.
                # This would mean that we can perform some fights, if it is present, we also check to
                # see how much time until the attacks reset, once the current time has surpassed that
                # value, we allow another notification to be sent.
                if not self.goto_clan():
                    return False

                self.click(point=self.locs.clan_raid, pause=4)

                if self.grabber.search(self.images.raid_fight, bool_only=True):
                    # Fights are available, lets also parse out the next time that attacks will be reset.
                    self.props.next_raid_attack_reset = self.stats.get_raid_attacks_reset()
                    if not self.props.next_raid_attack_reset:
                        self.logger.info("The next raid attack reset could not be parsed correctly, a notification will not be sent...")

                    # Send out a notification to the user through Twilio.
                    notification = send_raid_notification(
                        sid=self.configuration.raid_notifications_twilio_account_sid,
                        token=self.configuration.raid_notifications_twilio_auth_token,
                        from_num=self.configuration.raid_notifications_twilio_from_number,
                        to_num=self.configuration.raid_notifications_twilio_to_number)

                    self.logger.info("a notification has been sent to {to_num} from {from_num}".format(
                        to_num=self.configuration.raid_notifications_twilio_to_number,
                        from_num=self.configuration.raid_notifications_twilio_from_number))

                    self.logger.info("message sid: {sid}".format(sid=notification.sid))
                    self.logger.info("message body: {body}".format(body=notification.body))
                    self.logger.info("the next notification will only be sent after the current raid attack reset has been reached...")
                    self.logger.info("next raid attack reset: {next_raid_attack}".format(next_raid_attack=self.props.next_raid_attack_reset))
                else:
                    self.logger.info("no raid fight is currently active or available! No notification will be sent.")

                self.calculate_next_raid_notifications_check()

    @wrap_current_function
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
            if force or timezone.now() > self.props.next_clan_results_parse:
                self.logger.info("{force_or_initiate} clan results parsing now.".format(
                    force_or_initiate="forcing" if force else "beginning"))

                # The clan results parse should take place.
                if not self.no_panel():
                    return False
                if not self.leave_boss():
                    return False

                # Travel to the clan page and attempt to parse out some generic
                # information about the current users clan.
                if not self.goto_clan():
                    return False

                # Is the user in a clan or not? If no clan is present,
                # exiting early and not attempting to parse.
                if not self.grabber.search(self.images.clan_info, bool_only=True):
                    self.logger.warning("no clan is available to parse, giving up...")

                # A clan is available, begin by opening the information panel
                # to retrieve some generic information about the clan.
                self.click(point=self.locs.clan_info, pause=2)

                self.logger.info("attempting to parse out generic clan information now...")

                # The clan info panel is open and we can attempt to grab the name and code
                # of the users current clan.
                name, code = self.stats.clan_name_and_code()

                if not name:
                    self.logger.warning("unable to parse clan name, giving up...")
                    return False
                if not code:
                    self.logger.warning("unable to parse clan code, giving up...")
                    return False

                # Getting or creating the initial clan objects. Updating the clan name
                # if it's changed since the last results parse, the code may not change.
                try:
                    clan = Clan.objects.get(code=code)
                except Clan.DoesNotExist:
                    clan = Clan.objects.create(code=code, name=name)

                if clan.name != name:
                    self.logger.info("clan name: {orig_name} has changed to {new_name}, updating clan information.".format(
                        orig_name=clan.name, new_name=name))
                    clan.name = name
                    clan.save()

                self.logger.info("{clan} was parsed successfully.".format(clan=clan))

                # At this point, the clan has been grabbed, safe to leave the information
                # panel and begin the retrieval of the current raid results.
                self.click(point=self.locs.clan_info_close, pause=1)

                self.logger.info("attempting to parse out most recent raid results from clan...")

                self.click(point=self.locs.clan_results, pause=2)
                self.click(point=self.locs.clan_results_copy, pause=1)

                win32clipboard.OpenClipboard()
                results = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                if not results:
                    self.logger.warning("no clipboard data was retrieved, giving up...")
                    return False

                # Attempting to generate the raid result for logging purposes,
                # if the raid found already exists, we'll simply return a False
                # boolean to determine this and log some info.
                raid = RaidResult.objects.generate(clipboard=results, clan=clan, instance=self.instance)

                if not raid:
                    self.logger.warning("the parsed raid results already exist and likely haven't changed since the last parse.")
                else:
                    self.logger.info("successfully parsed and created a new raid result instance.")
                    self.logger.info("raid result: {raid}".format(raid=raid))

                self.calculate_next_clan_result_parse()

    def ad(self):
        """
        Collect ad if one is available on the screen.

        Note: This function does not require a max loop (FUNCTION_LOOP_TIMEOUT) since it only ever loops
              while the collect panel is on screen, this provides only two possible options.

        This is the main ad function. Used in two places:
           - One instance is used by the transition functionality and decorator.
           - The other one allows the function to be called directly without decorators added.
        """
        while self.grabber.search(self.images.collect_ad, bool_only=True) or self.grabber.search(self.images.watch_ad, bool_only=True):
            if self.configuration.enable_premium_ad_collect:
                self.logger.info("collecting premium ad!")
                self.click(point=self.locs.collect_ad, pause=1, offset=1)
            else:
                self.logger.info("watching normal ad!")
                self.click(point=self.locs.collect_ad, offset=1)

                # An ad has been launched... Let's wait a while before attempting to close it.
                sleep(30)

                # Ad likely finished at this point, attempt to close the ad now by using the
                # back button within the emulator.
                self.logger.info("attempting to close watched ad.")
                self.click(point=self.locs.back_emulator, pause=3)
                self.click(point=self.locs.collect_ad_after_watch, pause=2)

            self.stats.statistics.bot_statistics.premium_ads += 1
            self.stats.statistics.bot_statistics.save()

    @wrap_current_function
    @not_in_transition
    def collect_ad(self):
        self.ad()

    def collect_ad_no_transition(self):
        self.ad()

    @not_in_transition
    def fight_boss(self):
        """
        Ensure that the boss is being fought if it isn't already.
        """
        loops = 0
        while True:
            loops += 1
            if loops == BOSS_LOOP_TIMEOUT:
                self.logger.warning("unable to enter boss fight currently...")
                self.ERRORS += 1
                return False

            if self.grabber.search(self.images.fight_boss, bool_only=True):
                self.logger.info("attempting to initiate boss fight in game. ({tries}/{max})".format(tries=loops, max=BOSS_LOOP_TIMEOUT))
                self.click(point=self.locs.fight_boss, pause=0.8)
            else:
                break

        return True

    @not_in_transition
    def leave_boss(self):
        """
        Ensure that there is no boss being fought (avoids transition).
        """
        loops = 0
        while True:
            loops += 1
            if loops == BOSS_LOOP_TIMEOUT:
                self.logger.warning("unable to leave boss fight, assuming boss could not be reached...")
                self.ERRORS += 1
                return True

            if not self.grabber.search(self.images.fight_boss, bool_only=True):
                self.logger.info("attempting to leave active boss fight in game. ({tries}/{max})".format(
                    tries=loops, max=BOSS_LOOP_TIMEOUT))
                self.click(point=self.locs.fight_boss, pause=0.8)
            else:
                break

        # Sleeping for a bit after leaving boss fight in case some sort of
        # transition takes places directly after.
        sleep(3)
        return True

    @wrap_current_function
    @not_in_transition
    def tap(self):
        """
        Perform simple screen tap over entire game area.
        """
        if self.configuration.enable_tapping:
            self.logger.info("tapping!")
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
                self.click(point=point)

            # If no transition state was found during clicks, wait a couple of seconds in case a fairy was
            # clicked just as the tapping ended.
            sleep(2)

    @wrap_current_function
    @not_in_transition
    def activate_skills(self, force=False):
        """
        Activate any skills off of cooldown, and determine if waiting for longest cd to be done.
        """
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
                    self.logger.info("skills will only be activated once {key} is ready.".format(key=skills[0][1]))
                    self.logger.info("{key} will be ready in {time}.".format(key=skills[0][1], time=strfdelta(attr - now)))
                    return

            # If this point is reached, ensure no panel is currently active, and begin skill activation.
            if not self.no_panel():
                return False

            self.logger.info("activating skills in game now.")
            for skill in skills:
                self.logger.info("activating {skill} now.".format(skill=skill[1]))
                self.click(point=getattr(self.locs, skill[1]), pause=0.2)

            # Recalculate all skill execution times.
            self.calculate_skill_execution()
            return True

    @not_in_transition
    def goto_panel(self, panel, icon, top_find, bottom_find, collapsed=True, top=True):
        """
        Goto a specific panel, panel represents the key of this panel, also used when determining what panel
        to click on initially.

        Icon represents the image in game that represents a panel being open. This image is searched
        for initially before attempting to move to the top or bottom of the specified panel.

        NOTE: This function will return a boolean to determine if the panel was reached successfully. This can be
              used to exit out of actions or other pieces of bot functionality early if something has gone wrong.
        """
        self.logger.debug("attempting to travel to the {collapse_expand} {top_bot} of {panel} panel".format(
            collapse_expand="collapsed" if collapsed else "expanded", top_bot="top" if top else "bottom", panel=panel))

        loops = 0
        while not self.grabber.search(icon, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("error occurred while travelling to {panel} panel, exiting function early.".format(panel=panel))
                self.ERRORS += 1
                return False

            self.click(point=getattr(self.locs, panel), pause=1)

        # At this point, the panel should at least be opened.
        find = top_find if top or bottom_find is None else bottom_find

        # Trying to travel to the top or bottom of the specified panel, trying a set number of times
        # before giving up and breaking out of loop.
        loops = 0
        end_drag = self.locs.scroll_top_end if top else self.locs.scroll_bottom_end
        while not self.grabber.search(find, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("error occurred while travelling to {panel} panel, exiting function early.".format(panel=panel))
                self.ERRORS += 1
                return False

            # Manually wrap self.drag function in the not_in_transition call, ensure that
            # un-necessary mouse drags are not performed.
            self.drag(start=self.locs.scroll_start, end=end_drag, pause=1)

        # The shop panel may not be expanded/collapsed. Skip when travelling to shop panel.
        if panel != "shop":
            # Ensure the panel is expanded/collapsed appropriately.
            loops = 0
            if collapsed:
                while not self.grabber.search(self.images.expand_panel, bool_only=True):
                    loops += 1
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("unable to collapse panel: {panel}, exiting function early.".format(panel=panel))
                        self.ERRORS += 1
                        return False
                    self.click(point=self.locs.expand_collapse_top, pause=1, offset=1)
            else:
                while not self.grabber.search(self.images.collapse_panel, bool_only=True):
                    loops += 1
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("unable to expand panel: {panel}, exiting function early.".format(panel=panel))
                        self.ERRORS += 1
                        return False
                    self.click(point=self.locs.expand_collapse_bottom, pause=1, offset=1)

        # Reaching this point represents a successful panel travel to.
        return True

    def goto_master(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the sword master panel.
        """
        return self.goto_panel("master", self.images.master_active, self.images.raid_cards, self.images.prestige, collapsed=collapsed, top=top)

    def goto_heroes(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the heroes panel.
        """
        return self.goto_panel("heroes", self.images.heroes_active, self.images.masteries, self.images.maya_muerta, collapsed=collapsed, top=top)

    def goto_equipment(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the heroes panel.
        """
        return self.goto_panel("equipment", self.images.equipment_active, self.images.crafting, None, collapsed=collapsed, top=top)

    def goto_pets(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the pets panel.
        """
        return self.goto_panel("pets", self.images.pets_active, self.images.next_egg, None, collapsed=collapsed, top=top)

    def goto_artifacts(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the artifacts panel.
        """
        return self.goto_panel("artifacts", self.images.artifacts_active, self.images.salvaged, None, collapsed=collapsed, top=top)

    def goto_shop(self, collapsed=False, top=True):
        """
        Instruct the bot to travel to the shop panel.
        """
        return self.goto_panel("shop", self.images.shop_active, self.images.shop_keeper, None, collapsed=collapsed, top=top)

    @not_in_transition
    def goto_clan(self):
        """
        Open the clan panel in game.
        """
        self.logger.info("attempting to open the clan panel in game.")

        loops = 0
        while not self.grabber.search(self.images.clan, bool_only=True):
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.info("unable to open clan panel, giving up.")
                return False

            loops += 1
            self.click(point=self.locs.clan)
            sleep(3)

        return True

    @not_in_transition
    def no_panel(self):
        """
        Instruct the bot to make sure no panels are currently open.
        """
        loops = 0
        while self.grabber.search(self.images.exit_panel, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("error occurred while attempting to close all panels, exiting early.")
                self.ERRORS += 1
                return False

            self.click(point=self.locs.close_bottom, offset=2)
            if not self.grabber.search(self.images.exit_panel, bool_only=True):
                break

            self.click(point=self.locs.close_top, offset=2)
            if not self.grabber.search(self.images.exit_panel, bool_only=True):
                break

        return True

    @wrap_current_function
    def soft_shutdown(self):
        """
        Perform a soft shutdown of the bot, taking care of any cleanup or related tasks.
        """
        self.logger.info("beginning soft shutdown...")
        self.update_stats(force=True)

    @wrap_current_function
    def pause(self):
        """
        Execute a pause for this Bot.
        """
        self.PAUSE = True
        self.instance.pause()

    @wrap_current_function
    def resume(self):
        """Execute a resume for this Bot."""
        self.PAUSE = False
        self.instance.resume()

    @wrap_current_function
    def terminate(self):
        """
        Execute a termination of this Bot instance.
        """
        self.TERMINATE = True

    @wrap_current_function
    def soft_terminate(self):
        """
        Execute a soft shutdown/termination of this Bot instance.
        """
        self.soft_shutdown()
        self.TERMINATE = True

    @wrap_current_function
    def setup_shortcuts(self):
        """
        Setup the keypress shortcut listener.
        """
        self.logger.info("initiating keyboard (shortcut) listener...")
        # Attach the ShortcutListener callback function that is called whenever a key is pressed.
        listener = ShortcutListener(logger=self.logger, instance=self.instance, cooldown=2)

        keyboard.on_press(callback=listener.on_press)
        keyboard.on_release(callback=listener.on_release)

    @wrap_current_function
    def setup_loop_functions(self):
        """
        Generate list of loop functions based on the enabled functions specified in the configuration.
        """
        lst = [
            k for k, v in {
                "goto_master": True,
                "fight_boss": True,
                "clan_crate": True,
                "tap": self.configuration.enable_tapping,
                "collect_ad": True,
                "parse_current_stage": True,
                "prestige": self.configuration.enable_auto_prestige,
                "daily_achievement_check": self.configuration.enable_daily_achievements,
                "raid_notifications": self.configuration.enable_raid_notifications,
                "clan_results_parse": self.configuration.enable_clan_results_parse,
                "actions": True,
                "activate_skills": self.configuration.enable_skills,
                "update_stats": self.configuration.enable_stats,
                "recover": True,
                "breaks": self.configuration.enable_breaks
            }.items() if v
        ]

        self.logger.info("loop functions have been setup...")
        self.logger.info("{loop_funcs}".format(loop_funcs=", ".join(lst)))
        return lst

    @wrap_current_function
    def restart_emulator(self, wait=30):
        """
        Restart the emulator.
        """
        self.logger.info("attempting to restart the emulator...")
        self.click(point=EMULATOR_LOCS[self.configuration.emulator]["close_emulator"], pause=1)

        loops = 0
        while self.grabber.search(self.images.restart, bool_only=True):
            loops += 1
            found, pos = self.grabber.search(self.images.restart)
            if found:
                self.logger.info("restarting emulator now...")
                click_on_image(self.images.restart, pos)
                sleep(wait)
                return True

            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warn("unable to restart emulator...")
                return False

    @wrap_current_function
    def open_game(self, wait=40):
        """
        Open the game from the main emulator screen.
        """
        self.logger.info("opening tap titans 2 now...")

        loops = 0
        while not self.grabber.search(self.images.tap_titans_2, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warn("unable to open game...")
                return False

            # Sleep for a while after each check...
            sleep(2)

        found, pos = self.grabber.search(self.images.tap_titans_2)
        if found:
            self.logger.info("game launcher was found, starting game...")
            click_on_image(self.images.tap_titans_2, pos)
            sleep(wait)
            return True

    @wrap_current_function
    def initialize(self):
        """
        Run any initial functions as soon as a session is started.
        """
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
        if self.configuration.raid_notifications_check_on_start:
            self.raid_notifications(force=True)

    @wrap_current_function
    def run(self):
        """
        A run encapsulates the entire bot runtime process into a single function that conditionally
        checks for different things that are currently happening in the game, then launches different
        automated action within the emulator.
        """
        try:
            self.setup_shortcuts()
            self.goto_master()
            self.initialize()

            # Update the initial bots artifacts information that is used when upgrading
            # artifacts in game. This is handled after stats have been updated.
            self.owned_artifacts = self.get_upgrade_artifacts()

            if self.configuration.upgrade_owned_artifacts:
                self.next_artifact_index = 0
                self.update_next_artifact_upgrade()

            # Setup main game loop variables.
            loop_funcs = self.setup_loop_functions()

            # Generating an initial datetime that will be checked when the bot has been paused.
            # If this datetime is surpassed when the pause functionality is checked, a log will be sent.
            # Otherwise, we continue the loop normally.
            pause_log_dt = timezone.now() + datetime.timedelta(seconds=5)

            # Main game loop.
            while True:
                for func in loop_funcs:
                    # Any explicit functions can be executed after the main game loop has finished.
                    # The Queue handles the validation to ensure only available functions can be created...
                    for qfunc in Queue.objects.filter(instance=self.instance).order_by("-created"):
                        if qfunc.function not in QUEUEABLE_FUNCTIONS:
                            self.logger.info("queued function: {func} encountered but this function does not exist on the bot... ignoring function!".format(
                                func=qfunc.function))

                            qfunc.finish()
                            continue

                        self.logger.info("queued function: {func} will be executed!".format(func=qfunc.function))
                        # Executing the function directly on the Bot. We can force the function if it requires it to be ran manually.
                        wait = wait_afterwards(
                            function=getattr(self, qfunc.function),
                            floor=self.configuration.post_action_min_wait_time,
                            ceiling=self.configuration.post_action_max_wait_time
                        )

                        if qfunc.function in FORCEABLE_FUNCTIONS:
                            wait(force=True)
                        else:
                            wait()

                        qfunc.finish()

                    if self.TERMINATE:
                        self.logger.info("terminate signal encountered, exiting...")
                        raise TerminationEncountered()
                    if self.PAUSE:
                        now = timezone.now()
                        if now > pause_log_dt:
                            pause_log_dt = now + datetime.timedelta(seconds=10)
                            self.logger.info("waiting for resume...")

                        # PAUSED. Continue loop forever unless resumed/stopped.
                        continue

                    wait_afterwards(getattr(self, func), floor=self.configuration.post_action_min_wait_time, ceiling=self.configuration.post_action_max_wait_time)()

        except TerminationEncountered:
            self.logger.info("manual termination encountered... terminating!")
        except FailSafeException:
            self.logger.info("failsafe termination encountered: terminating!")
        except Exception as exc:
            self.logger.critical("critical error encountered: {exc}".format(exc=exc), exc_info=True)
            self.logger.info("terminating!")
            if self.configuration.soft_shutdown_on_critical_error:
                self.logger.info("soft shutdown is enabled on critical error... attempting to shutdown softly...")
                self.soft_shutdown()

        # Cleaning up the BotInstance once a termination has been received.
        finally:
            self.stats.session.end = timezone.now()
            self.stats.session.save()
            self.instance.stop()
            Queue.flush()

            # Cleanup the keyboard listener to no longer use callbacks.
            keyboard.unhook_all()

            self.logger.info("==========================================================================================")
            self.logger.info("{session}".format(session=self.stats.session))
            self.logger.info("==========================================================================================")

            # Remove logging handles.
            self.logger.handlers = []

            # Update the users authentication reference to no longer be online.
            AuthWrapper().offline()
