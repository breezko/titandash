"""
stats.py

The stats module will encapsulate all functionality related to the stats
panel located inside of the heroes panel in game.
"""
from settings import __VERSION__
from tt2.core.maps import STATS_COORDS, STAGE_COORDS, CLAN_COORDS, ARTIFACT_TIER_MAP, IMAGES, GAME_LOCS, PRESTIGE_COORDS
from tt2.core.constants import (
    STATS_JSON_TEMPLATE, STATS_GAME_STAT_KEYS, STATS_BOT_STAT_KEYS, LOGGER_FILE_NAME, STATS_DATE_FMT,
    CLAN_PLAYER_MAP, STATS_DATETIME_FMT
)
from tt2.core.utilities import convert, diff, click_on_point, match

from PIL import Image

import datetime
import pytesseract
import cv2
import numpy as np
import uuid
import json

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"

_KEY_MAP = {
    "game_statistics": STATS_GAME_STAT_KEYS,
    "bot_statistics": STATS_BOT_STAT_KEYS,
}


class OCRParseError(Exception):
    pass


class ClanNotFoundError(Exception):
    pass


class ClanTimestampNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class Stats:
    """Stats class contains all possible stat values and can be updated dynamically."""
    def __init__(self, grabber, config, stats_file, logger):
        self.logger = logger
        self._base()

        # Game statistics.
        for key in STATS_GAME_STAT_KEYS:
            setattr(self, key, 0)

        # Bot statistics.
        for key in STATS_BOT_STAT_KEYS:
            setattr(self, key, 0)

        # Prestige statistics initializing as empty.
        self.prestige_statistics = {
            "prestiges": [],
            "statistics": {}
        }

        # Artifacts objects initializing as empty.
        self.artifact_statistics = {
            "discovered": "0/95",
            "artifacts": {}
        }
        for k, v in ARTIFACT_TIER_MAP.items():
            self.artifact_statistics["artifacts"][k] = {}
            for k1 in v:
                self.artifact_statistics["artifacts"][k][k1] = False

        # Clan statistics initializing as empty.
        self.clan_statistics = {}

        # Session statistics.
        self.started = datetime.datetime.now()
        self.day = datetime.datetime.strftime(self.started, STATS_DATE_FMT)
        self.last_update = self.started
        self.config = config

        # Grabber is used to perform OCR updates when grabbing game statistics.
        self.grabber = grabber

        # Generate a key that matches the currently specified height and width that's configured.
        # Key is used by the update method to grab proper regions when taking screenshots.
        self.key = "{0}x{1}".format(self.grabber.width, self.grabber.height)

        # File name specified by configurations.
        self.file = stats_file
        self.content = self.retrieve()

        # Additionally, including a session id here that may be appended to the stats file
        # if the id isn't already present, this allows the configuration options being used
        # to be stored alongside any extra information about the bots runtime.
        self.session = str(uuid.uuid4())
        self.session_data = None

        # Log file associated with current stats session.
        self.log_file = LOGGER_FILE_NAME
        # Version of Bot running this current session.
        self.version = __VERSION__

        # Update instance to reflect any available values in the content attr.
        self.update_from_content()

    @property
    def highest_stage(self):
        """Retrieve the highest stage reached from game stats, returning None if it is un parsable."""
        stat = getattr(self, "highest_stage_reached")
        value = convert(getattr(self, "highest_stage_reached"))
        self.logger.debug("Highest stage parsed: {before} -> {after}".format(before=stat, after=value))

        try:
            return int(value)
        except ValueError:
            return None

    def _base(self):
        """Manually set every expected value, allows for easier access later on."""
        self.premium_ads = None
        self.clan_ship_battles = None
        self.actions = None
        self.updates = None

    def _process(self, scale=3, iterations=1, image=None, current=False, region=None):
        """Process the grabbers current image before OCR extraction attempt."""
        if current:
            self.grabber.snapshot(region=region)
        if image:
            image = image
        else:
            image = self.grabber.current

        image = np.array(image)

        # Resize and desaturate.
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply dilation and erosion.
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=iterations)
        image = cv2.erode(image, kernel, iterations=iterations)

        return Image.fromarray(image)

    def _process_stage(self, scale=5, threshold=100, image=None):
        if image:
            image = image
        else:
            image = self.grabber.current

        image = np.array(image)

        # Resize image.
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        # Create gray scale.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Perform threshold on image.
        retr, mask = cv2.threshold(image, 230, 255, cv2.THRESH_BINARY)

        # Find contours.
        contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw black over counters smaller than 200, removing un wanted blobs from stage image.
        for contour in contours:
            if cv2.contourArea(contour) < threshold:
                cv2.drawContours(mask, [contour], 0, (0,), -1)

        return Image.fromarray(mask)

    def stat_diff(self, ctx):
        """
        Determine the difference between the game stats instance attribute values, and the original
        values that were captures when the instance was initialized.

        ctx Should equal a value present in the global _X_STAT_KEYS that are used to determine what values are diffed.
        """
        keys = _KEY_MAP[ctx]
        new_attrs = {key: getattr(self, key, 0) for key in keys}
        old_attrs = {key: self.content.get(ctx).get(key, 0) for key in keys}

        new_attrs_converted = {}
        old_attrs_converted = {}
        # Is the value formatted with a conversion key? (i.e: K, M).
        for key, value in new_attrs.items():
            new_attrs_converted[key] = convert(value)

        for key, value in old_attrs.items():
            old_attrs_converted[key] = convert(value)

        # Session stats should also contain relevant information about the difference between initial
        # values, and the current values of the game.
        return {
            key:
                {
                    "old": old_attrs.get(key),
                    "new": new_attrs.get(key),
                    "diff": diff(old_attrs_converted.get(key, 0), new_attrs_converted.get(key, 0))
                }
            for key in keys
        }

    def as_json(self, update_artifacts=False):
        """Convert the stats instance into a JSON compliant dictionary."""
        sessions = self.content.get("sessions")
        if sessions.get(self.day):
            sessions[self.day][self.session] = {
                "version": self.version,
                "start_date": str(self.started),
                "last_update": str(self.last_update),
                "log_file": self.log_file,
                "game_stat_differences": self.stat_diff("game_statistics"),
                "bot_stat_differences": self.stat_diff("bot_statistics"),
                "config": vars(self.config)
            }
        else:
            sessions[self.day] = {
                self.session: {
                    "version": self.version,
                    "start_date": str(self.started),
                    "last_update": str(self.last_update),
                    "log_file": self.log_file,
                    "game_stat_differences": self.stat_diff("game_statistics"),
                    "bot_stat_differences": self.stat_diff("bot_statistics"),
                    "config": vars(self.config)
                }
            }

        # If artifact update has been specified, update the artifacts on the stats instance.
        # Any previous artifact data will be present and may speed up processing as more are
        # unlocked.
        if update_artifacts:
            self.parse_artifacts()

        # Create final dictionary of all of game statistics.
        stats = {
            "game_statistics": {key: getattr(self, key, "None") for key in STATS_GAME_STAT_KEYS},
            "bot_statistics": {key: getattr(self, key, "None") for key in STATS_BOT_STAT_KEYS},
            "prestige_statistics": self.prestige_statistics,
            "artifact_statistics": self.artifact_statistics,
            "clan_statistics": self.clan_statistics,
            "sessions": sessions
        }
        return stats

    def parse_artifacts(self):
        """
        Parse artifacts in game through OCR, need to make use of mouse dragging here to make sure that all possible
        artifacts have been set to found/not found. This is an expensive function through the image recognition.

        Note that dragging will not be a full drag (all artifacts from last drag, now off of the screen). To make sure
        that missed artifacts have a chance to go again.

        Additionally, this method expects that the game screen is at the top of the expanded artifacts screen.
        """
        from tt2.core.maps import ARTIFACT_TIER_MAP, ARTIFACT_MAP, GAME_LOCS, IMAGES
        from tt2.core.utilities import sleep
        from tt2.core.utilities import drag_mouse

        # Game locations based on current size of game.
        locs = GAME_LOCS["GAME_SCREEN"]
        images = IMAGES["GENERIC"]

        # Region to search for the final artifact, taken from the configuration file.
        last_artifact_region = GAME_LOCS["ARTIFACTS"]["bottom_region"]

        # Looping forever until the bottom artifact has been found.
        break_next = False
        while True:
            for tier, d in ARTIFACT_TIER_MAP.items():
                for artifact, path in d.items():
                    # Break early if the artifact has already been discovered.
                    if self.artifact_statistics["artifacts"][tier][artifact]:
                        continue

                    try:
                        # Do a quick check to ensure that the artifacts screen is still open (no transition state).
                        while not self.grabber.search(images["artifacts_active"], bool_only=True):
                            continue

                        if self.grabber.search(path, bool_only=True):
                            self.logger.info("Artifact: {artifact} was successfully found, marking as owned".format(
                                artifact=artifact))
                            self.artifact_statistics["artifacts"][tier][artifact] = True

                    except ValueError:
                        self.logger.error("Artifact: {artifact} could not be searched for, leaving false".format(
                            artifact=artifact))

            if break_next:
                self.logger.info("Artifact: {artifact} was found at the bottom of the screen, exiting parse loop "
                                 "now".format(artifact=self.config.BOTTOM_ARTIFACT))
                break

            # Scroll down slightly and check for artifacts again.
            drag_mouse(locs["scroll_start"], locs["scroll_bottom_end"], quick_stop=locs["scroll_quick_stop"])
            sleep(1)

            # Checking at the end of the loop to break, one more loop takes place before exit.
            if self.grabber.search(ARTIFACT_MAP.get(self.config.BOTTOM_ARTIFACT), region=last_artifact_region,
                                   bool_only=True):
                break_next = True

        # Do a loop to update the discovered artifacts in game.
        discovered = 0
        for tier, d in ARTIFACT_TIER_MAP.items():
            for artifact, path in d.items():
                if self.artifact_statistics["artifacts"][tier][artifact]:
                    discovered += 1

        self.artifact_statistics["discovered"] = "{discovered}/95".format(discovered=discovered)

    def _get_clan(self, code):
        for key in self.clan_statistics:
            if code in key:
                return key, self.clan_statistics[key]

        raise ClanNotFoundError()

    @staticmethod
    def _get_clan_stats(clan, key):
        for timestamp in clan:
            if timestamp == key:
                return key, clan[key]

        raise ClanTimestampNotFoundError("Timestamp: {timestamp} isn't present in clan statistics".format(timestamp=key))

    @staticmethod
    def _get_user_from_stats(stats, key):
        """
        Attempt to grab a user from a clan statistics instance. In case of a username change. we can grab based on
        the id of the user.
        """
        data = None
        try:
            data = stats["users"][key]
        except KeyError:
            key = key.split("-")
            key[1] = key[1].replace(" ", "")
            for user_key in stats["users"]:
                for piece in key:
                    if piece in user_key:
                        data = stats["users"][user_key]

        if data:
            return data
        else:
            raise UserNotFoundError()

    def compare_clan_stats(self, code, keys):
        """
        Attempt to compare the two given parse keys for the specified clan. Determining some interesting data points to
        see how much of a difference between the oldest->newest key.
        """
        try:
            clan_key, clan = self._get_clan(code=code)
            stats_key_old, stats_old = self._get_clan_stats(clan, keys[0])
            stats_key_new, stats_new = self._get_clan_stats(clan, keys[1])
        except ClanNotFoundError:
            self.logger.error("Clan with code: {code} couldn't be found.".format(code=code))
            return
        except ClanTimestampNotFoundError as exc:
            self.logger.error(exc)
            return

        self.logger.info("========================================")
        self.logger.info("COMPARING {clan} STATISTICS FROM {timestamp_old} -> {timestamp_new}".format(
            clan=clan_key, timestamp_old=stats_key_old, timestamp_new=stats_key_new))

        compared = {"users": {}}
        # Begin comparing the clan statistics from both parsings.
        for key, options in CLAN_COORDS["info"].items():
            if options[1] == int:
                old = int(stats_old[key])
                new = int(stats_new[key])
                difference = stats_new[key] - stats_old[key]
                compared[key] = {"old": old, "new": new, "difference": difference}
                self.logger.info(" -> {key}: {difference}".format(key=key, difference=difference))

        # Let's loop through each user.. Determining the difference of values and including
        # in the compared dictionary.
        self.logger.info("========================================")
        self.logger.info("BEGINNING COMPARISON'S OF USERS IN CLAN")
        for user_key in stats_new["users"].keys():
            self.logger.info("ATTEMPTING TO COMPARE {user}".format(user=user_key))
            compared["users"][user_key] = {}

            try:
                user_old = self._get_user_from_stats(stats=stats_old, key=user_key)
                user_new = self._get_user_from_stats(stats=stats_new, key=user_key)
            except UserNotFoundError:
                self.logger.error("COULD NOT GET USER: {user}... SKIPPING".format(user=user_key))
                continue

            for key, options in CLAN_PLAYER_MAP.items():
                if options[1] == int:
                    old = int(user_old[key])
                    new = int(user_new[key])
                    difference = new - old
                    compared["users"][user_key][key] = {"old": old, "new": new, "difference": difference}
                    self.logger.info(" -> {key}: {difference}".format(key=key, difference=difference))

            # Has the user's username changed? Any additional attributes
            # that should be parsed separately can be done here.
            old_username = user_old["username"]
            new_username = user_new["username"]
            if new_username != old_username:
                compared["users"][user_key]["username"] = {"old": old_username, "new": new_username}

            self.logger.info("========================================")

        # Clan comparison has finished, update clan statistics before writing.
        compared_key = "{old_timestamp} to {new_timestamp}".format(old_timestamp=stats_key_old, new_timestamp=stats_key_new)
        self.clan_statistics[clan_key].setdefault("comparisons", {})[compared_key] = compared

        self.logger.info("CLAN COMPARISON HAS FINISHED...")
        self.write()

    def _try_to_convert(self, options, scale=4, tries=10):
        """
        Attempt to convert the grabbers current image and coerce the returned value into the specified type.

        If we want an image to be coerced into an integer but the OCR keeps on returning "c" instead of 3 for example,
        we can continue to blow up the image until we get the correctly coerced values.
        """
        config = "--psm 7 nobatch digits" if options[1] == int else "--psm 7"
        max_tries = tries
        tries = 0
        while tries != max_tries:
            try:
                parsed = pytesseract.image_to_string(self._process(scale=scale), config=config)
                parsed = options[1](parsed)
                if options[1] == str:
                    if parsed == "":
                        raise OCRParseError("Parsed an empty string.")
                return parsed
            except ValueError:
                tries += 1
                scale += 1

        raise OCRParseError("Unable to parse value from image.")

    def clan_manual(self, timestamp):
        """
        Begin a manual parse of a specific clan.

        If a value parse fails, allowing the user to manually enter the value.
        """
        data = {key: None for key in CLAN_COORDS["info"]}
        data["users"] = {}

        # Begin attempting to grab clan information using the configured coordinates and options
        # for each data point. The location of these elements don't ever change so we can safely
        # parse these using static coordinate locations.
        for key, options in CLAN_COORDS["info"].items():
            try:
                self.grabber.snapshot(region=options[0])
                data[key] = self._try_to_convert(options=options)
            except OCRParseError:
                self.logger.info("")
                data[key] = options[1](input("{key} COULDN'T BE PARSED. ENTER MANUALLY: ".format(key=key.upper())))

            self.logger.info(" -> {key}: {value}".format(key=key, value=data[key]))

        # Set our stats data in the current clan statistics for this clan.
        self.clan_statistics.setdefault(data["code"], {})[timestamp] = data
        return data

    def player_manual(self, clan_key, timestamp, cache):
        """
        Begin a manual parse of a specific clan member.

        If any None values are present after the user is parsed, they may be manually
        fixed up by the user.
        """
        player = self._get_player_ocr()
        raid = self._get_raid_ocr()

        data = "{player}\n{raid}".format(player=player, raid=raid)
        data = [ln.lower() for ln in data.split("\n") if ln not in ["\n", "", " ", "  "]]
        stats = {k: None for k in CLAN_PLAYER_MAP.keys()}

        for line in data:
            parse = []
            for key, options in CLAN_PLAYER_MAP.items():
                if stats[key] is not None:
                    continue

                try:
                    # Begin by trying to generate the expected key from the list of options
                    # for this data point.
                    # (ie: max_prestige_stage -> `"Max Prestige Stage" in "Max Prestige Stage 51503"`).
                    parse = line.split(" ")
                    find = key.replace("_", " ")
                    if key == "id":
                        find = find + ":"

                    if find in line:
                        # Replacing a specific character in the expected value.
                        # This happens when parsing a value like the highest tournament rank.
                        # (ie: #1 -> 1).
                        if len(options) > 2:
                            stats[key] = options[1](parse[options[0]].replace(options[2], ""))
                            break

                        # Default behaviour will coerce the value into the type defined in options.
                        if type(options[0]) != int and len(options[0]) > 1:
                            stats[key] = ' '.join(parse[options[0][0]:options[0][1]])
                        else:
                            stats[key] = options[1](parse[options[0]])

                        # If the current parsed value has already been cached and fixed... We can use the fixed value
                        # instead of the one that would need to be manually fixed up.
                        try:
                            if parse[options[0]] in cache.get(key, {}).keys():
                                stats[key] = cache[key][parse[options[0]]]
                        except IndexError:
                            pass
                        except TypeError:
                            pass

                # If an exception occurs, it's okay to skip this key, it's set to None and we can check for None
                # values after finishing our parsing and let the user manually fix them up.
                except Exception as exc:
                    self.logger.error(exc)
                    # Is the value present in the cache of incorrect -> correct values.
                    try:
                        if parse[options[0]] in cache.get(key, {}).keys():
                            stats[key] = cache[key][parse[options[0]]]
                        else:
                            # Setting the stats key to whatever the incorrect parsed value is.
                            # And it can be dealt with and fixed during parse fixup process.
                            stats[key] = [key, parse[options[0]], options[1]]
                    except IndexError:
                        pass
                    except TypeError:
                        pass
                    pass

        stats["rank"] = self._determine_clan_rank()
        stats["username"] = self._get_player_username()
        # Check to see if any data points are missing or weren't parsed properly.
        # (ie: str value == '', value == None).
        for key, value in {key: value for key, value in stats.items() if type(value) == list or value is None}.items():
            if value is None:
                value = []
            fix = input("'{key}' COULDN'T BE PARSED. ENTER MANUALLY: ".format(key=key))
            cache.setdefault(value[0], {})[value[1]] = value[2](fix)
            stats[key] = value[2](fix)

        # Are there any explicit value checks we can do in case of wrong values being parsed?
        if not match(string=stats["id"]):
            fix = input("'id' WAS PARSED INCORRECTLY. ENTER MANUALLY: ")
            cache.setdefault("id", {})[stats["id"]] = fix
            stats["id"] = fix

        if stats["username"] in cache.get("username", {}).keys():
            stats["username"] = cache["username"][stats["username"]]

        for key, value in stats.items():
            self.logger.info(" -> {key}: {value}".format(key=key, value=value))

        self.logger.info("PLEASE REVIEW PARSED VALUES. TYPE 'Y' TO CONTINUE. OR ENTER AN AVAILABLE KEY TO MODIFY THE VALUE.")
        val = None
        while val is None:
            val = input()
            if val.lower() == "y":
                break

            if val in stats:
                fix = CLAN_PLAYER_MAP.get(val, [None, str])[1](input("Modify '{val}' [{orig}]: ".format(val=val, orig=stats[val])))
                cache.setdefault(val, {})[stats[val]] = fix
                stats[val] = fix
            else:
                print("'{val}' is not available to modify".format(val=val))

            # Set value back to None when finished to loop until exit code ('y') is entered.
            val = None

        self.clan_statistics[clan_key][timestamp]["users"][stats["id"]] = stats
        self.clan_statistics["cache"] = cache

        # Additionally, let's exit the current players profile panel before exiting.
        while not self.grabber.search(IMAGES["CLAN_MEMBER"]["leave_clan"], bool_only=True):
            click_on_point(GAME_LOCS["CLAN"]["member_close"], pause=0.5)

        return stats, cache

    def _get_player_username(self):
        """
        Attempt to retrieve the players username by determining where it should
        be located based on different information present on the panel.
        """
        coord = CLAN_COORDS["member"]["username"]
        if self._manage_buttons_present():
            coord = (coord[0], coord[1] - 28, coord[2], coord[3] - 28)

        return pytesseract.image_to_string(self._process(current=True, region=coord), config="--psm 7 nobatch usernames")

    def _get_player_ocr(self):
        click_on_point(GAME_LOCS["CLAN"]["member_player_stats"], pause=1)
        return pytesseract.image_to_string(self._process(scale=3, current=True, region=CLAN_COORDS["member"]["panel"]), config="--psm 6 -l eng ")

    def _get_raid_ocr(self):
        click_on_point(GAME_LOCS["CLAN"]["member_raid_stats"], pause=1)
        return pytesseract.image_to_string(self._process(scale=3, current=True, region=CLAN_COORDS["member"]["panel"]), config="--psm 6 -l eng")

    def _determine_clan_rank(self):
        """Determine which rank a user is. This method assumes that a profile panel is open for a specific user."""
        for key, path in IMAGES["CLAN_MEMBER"]["ranks"].items():
            if self.grabber.search(path, bool_only=True):
                return key.replace("_", " ").title()

        # No rank could be parsed?
        return None

    def _manage_buttons_present(self):
        return self.grabber.search(IMAGES["CLAN_MEMBER"]["kick"], bool_only=True) \
               or self.grabber.search(IMAGES["CLAN_MEMBER"]["demote"], bool_only=True) \
               or self.grabber.search(IMAGES["CLAN_MEMBER"]["promote"], bool_only=True)

    def update_from_content(self):
        """Update self based on the JSON content taken from stats file."""
        game_stats = self.content.get("game_statistics")
        if game_stats:
            for key, value in game_stats.items():
                setattr(self, key, value)
                self.logger.debug("Stats.{attr}: {value}".format(attr=key, value=value))

        bot_stats = self.content.get("bot_statistics")
        if bot_stats:
            for key, value in bot_stats.items():
                setattr(self, key, value)
                self.logger.debug("Stats.{attr}: {value}".format(attr=key, value=value))

        prestige_stats = self.content.get("prestige_statistics")
        if prestige_stats:
            self.prestige_statistics = prestige_stats
            self.logger.debug("Prestige Statistics: {prestige_stats}".format(prestige_stats=prestige_stats))

        artifact_stats = self.content.get("artifact_statistics")
        if artifact_stats:
            for tier, d in artifact_stats["artifacts"].items():
                for artifact, value in artifact_stats["artifacts"][tier].items():
                    self.artifact_statistics["artifacts"][tier][artifact] = value
            self.artifact_statistics["discovered"] = artifact_stats["discovered"]
            self.logger.debug("Artifacts: {artifact_stats}".format(artifact_stats=artifact_stats))

        clan_stats = self.content.get("clan_statistics")
        if clan_stats:
            self.clan_statistics = clan_stats
            self.logger.debug("Clan Statistics: {clan_stats}".format(clan_stats=clan_stats))

        sessions = self.content.get("sessions")
        if sessions:
            if self.session in sessions:
                self.session_data = sessions[self.session]
            self.logger.debug("Sessions: {sessions}".format(sessions=sessions))

    def update_ocr(self, test_set=None):
        """
        Update the stats by parsing and extracting the text from the games stats page using the
        tesseract OCR engine to perform text parsing.

        Note that the current screen should be the stats page before calling this method.
        """
        for key, region in STATS_COORDS.items():
            if test_set:
                image = Image.open(test_set[key])
            else:
                self.grabber.snapshot(region=region)
                image = self._process()

            text = pytesseract.image_to_string(image, config='--psm 7')
            self.logger.debug("OCR result: {key} -> {text}".format(key=key, text=text))

            # The images do not always parse correctly, so we can attempt to parse out our expected
            # value from the STATS_COORD tuple being used.

            # Firstly, confirm that a number is present in the text result, if no numbers are present
            # at all, safe to assume the OCR has failed wonderfully.
            if not any(char.isdigit() for char in text):
                self.logger.warning("No digits found in OCR result, skipping key: {key}".format(key=key))
                continue

            # Otherwise, attempt to parse out the proper value.
            try:
                if len(text.split(':')) == 2:
                    value = text.split(':')[-1].replace(" ", "")
                else:
                    if key == "play_time":
                        value = " ".join(text.split(" ")[-2:])
                    else:
                        value = text.split(" ")[-1].replace(" ", "")

                # Finally, a small check to see that a value can successfully made into an
                # integer, float with either its last character taken off (K, M, %, etc).
                # This check is not required for the "play_time" key.
                if not key == "play_time":
                    try:
                        if not value[-1].isdigit():
                            try:
                                int(value[:-1])
                            except ValueError:
                                try:
                                    float(value[:-1])
                                except ValueError:
                                    continue

                        # Last character is a digit, value may be pure digit of some sort?
                        else:
                            try:
                                int(value)
                            except ValueError:
                                try:
                                    float(value)
                                except ValueError:
                                    continue
                    except IndexError:
                        self.logger.error(
                            "{key} - {value} could not be accessed parsed properly.".format(key=key, value=value))

                self.logger.info("Parsed value: {key} -> {value}".format(key=key, value=value))
                setattr(self, key, value)

            # Gracefully continuing loop if failure occurs.
            except ValueError:
                self.logger.error("Could not parse {key}: (OCR Result: {text})".format(key=key, text=text))

    def stage_ocr(self, test_image=None):
        """Attempt to parse out the current stage in game through an OCR check."""
        self.logger.debug("Attempting to parse out the current stage from in game")
        region = STAGE_COORDS["region"]

        if test_image:
            image = self._process_stage(scale=3, image=test_image)
        else:
            self.grabber.snapshot(region=region)
            image = self._process_stage(scale=3)

        text = pytesseract.image_to_string(image, config='--psm 7 nobatch digits')
        self.logger.debug("Parsed value: {text}".format(text=text))

        # Do some light parse work here to make sure only digit like characters are present
        # in the returned 'text' variable retrieved through tesseract.
        return ''.join(filter(lambda x: x.isdigit(), text))

    def update_prestige(self, test_image=None):
        """
        Right before a prestige takes place, we can generate and parse out some information from the screen
        present right before a prestige happens. This panel displays the time since the last prestige, we can store
        this, along with a timestamp for the prestige.

        A final stat can be modified as this is called to determine some overall statistics
        (# of prestige's, average time for prestige, etc)...

        This method expects the current in game panel to be the one right before a prestige takes place.
        """
        self.logger.debug("Attempting to parse out the time since last prestige")
        region = PRESTIGE_COORDS["time_since"]

        if test_image:
            image = self._process(scale=3, image=test_image)
        else:
            image = self._process(scale=3, current=True, region=region)

        text = pytesseract.image_to_string(image, config='--psm 7')
        self.logger.debug("Parsed value: {text}".format(text=text))

        # We now have the amount of time that this prestige took place, appending it to the list of prestiges
        # present in the statistics instance.
        hours, minutes, seconds = [int(t) for t in text.split(":")]
        self.prestige_statistics["prestiges"].append({
            "timestamp": datetime.datetime.now().strftime(STATS_DATETIME_FMT),
            "time": {
                "full": text,
                "total_seconds": datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()
            }
        })

        # Count, Total, Average...
        # Calculating the average time for each prestige in game for tracked prestiges.
        cnt = len(self.prestige_statistics["prestiges"])
        tot = 0

        for tracked in self.prestige_statistics["prestiges"]:
            tot += tracked["time"]["total_seconds"]

        avg = tot // cnt
        avg = str(datetime.timedelta(seconds=avg))

        self.prestige_statistics["statistics"] = {
            "prestige_count": len(self.prestige_statistics["prestiges"]),
            "average_prestige_time": avg
        }

        self.write()

    def retrieve(self):
        """Attempt to retrieve the stats JSON file with all current data."""
        try:
            # Open the stats file, parse data and set self attrs.
            with open(self.file) as file:
                return json.load(file)

        # If the file doesn't exist at all, build one.
        except EnvironmentError:
            self.build()

        # If the file is new, the json contents will not exist and throw a decode
        # error, new file template will be placed into the file and no retrieval.
        except json.JSONDecodeError:
            self.build()

        return self.retrieve()

    def build(self):
        """Build an empty JSON stats file, only used if one doesn't exist yet."""
        with open(self.file, "w+") as file:
            json.dump(STATS_JSON_TEMPLATE, file, indent=4)

    def write(self, update_artifacts=False):
        """Write the stats object to a JSON file, overwriting all old values in the process."""
        self.last_update = datetime.datetime.now()
        self.logger.info("Writing statistics to json file")
        contents = self.as_json(update_artifacts=update_artifacts)
        with open(self.file, "w+") as file:
            json.dump(contents, file, indent=4)

        self.logger.info("Stats were successfully written to {file}".format(file=self.file))
