"""
stats.py

The stats module will encapsulate all functionality related to the stats
panel located inside of the heroes panel in game.
"""
from settings import BOT_VERSION

from django.utils import timezone

from titandash.models.statistics import Statistics, PrestigeStatistics, ArtifactStatistics, Session, Log
from titandash.models.artifact import Artifact
from titandash.models.prestige import Prestige

from .maps import (
    STATS_COORDS, STAGE_COORDS, IMAGES, GAME_LOCS, PRESTIGE_COORDS,
    ARTIFACT_TIER_MAP, ARTIFACT_MAP, CLAN_COORDS, CLAN_RAID_COORDS
)
from .utilities import convert, delta_from_values

from PIL import Image

import datetime
import pytesseract
import cv2
import numpy as np
import uuid
import logging


class Stats:
    """Stats class contains all possible stat values and can be updated dynamically."""
    def __init__(self, instance, window, grabber, configuration, logger):
        self.instance = instance
        self.window = window
        self.logger = logger
        self.statistics = Statistics.objects.grab(instance=self.instance)

        # Statistics stored for differential calculations.
        self._old_game_stats = self.statistics.game_statistics
        self._old_bot_stats = self.statistics.bot_statistics

        # Prestige Statistics retrieved through database model.
        self.prestige_statistics = PrestigeStatistics.objects.grab(instance=instance)
        self.artifact_statistics = ArtifactStatistics.objects.grab(instance=instance)

        # Additionally, create a reference to the log file in question in the database so log files can
        # be retrieved directly from the dashboard and viewed.
        log_name = None
        for handle in self.logger.handlers:
            if type(handle) == logging.FileHandler:
                log_name = handle.baseFilename
                break

        if log_name:
            self.log = Log.objects.create(log_file=log_name)
        else:
            self.log = None

        # Generating a new Session to represent this instance being initialized.
        self.session = Session.objects.create(uuid=str(uuid.uuid4()), version=BOT_VERSION, start=timezone.now(), end=None, log=self.log, configuration=configuration, instance=self.instance)
        self.statistics.sessions.add(self.session)

        # Grabber is used to perform OCR updates when grabbing game statistics.
        self.grabber = grabber

        # Generate a key that matches the currently specified height and width that's configured.
        # Key is used by the update method to grab proper regions when taking screenshots.
        self.key = "{0}x{1}".format(self.grabber.width, self.grabber.height)
        self.version = BOT_VERSION

    @property
    def highest_stage(self):
        """
        Retrieve the highest stage reached from game stats, returning None if it is un parsable.
        """
        stat = self.statistics.game_statistics.highest_stage_reached
        value = convert(stat)
        self.logger.info("highest stage parsed: {before} -> {after}".format(before=stat, after=value))

        try:
            return int(value)
        except ValueError:
            return None
        except TypeError:
            return None

    def _process(self, scale=3, iterations=1, image=None, current=False, region=None):
        """
        Process the grabbers current image before OCR extraction attempt.
        """
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

    def parse_artifacts(self):
        """
        Parse artifacts in game through OCR, need to make use of mouse dragging here to make sure that all possible
        artifacts have been set to found/not found. This is an expensive function through the image recognition.

        Note that dragging will not be a full drag (all artifacts from last drag, now off of the screen). To make sure
        that missed artifacts have a chance to go again.

        Additionally, this method expects that the game screen is at the top of the expanded artifacts screen.
        """
        # from tt2.core.maps import ARTIFACT_TIER_MAP, ARTIFACT_MAP, GAME_LOCS, IMAGES
        from titandash.bot.core.utilities import sleep
        from titandash.bot.core.utilities import drag_mouse

        # Game locations based on current size of game.
        locs = GAME_LOCS["GAME_SCREEN"]
        images = IMAGES["GENERIC"]

        # Region to search for the final artifact, taken from the configuration file.
        last_artifact_region = GAME_LOCS["ARTIFACTS"]["bottom_region"]

        # Looping forever until the bottom artifact has been found.
        break_next = False
        while True:
            for tier, d in ARTIFACT_TIER_MAP.items():
                for artifact, values in d.items():
                    # Break early if the artifact has already been discovered.
                    art = self.artifact_statistics.artifacts.get(artifact=Artifact.objects.get(name=artifact))
                    if art.owned:
                        continue

                    try:
                        # Do a quick check to ensure that the artifacts screen is still open (no transition state).
                        while not self.grabber.search(images["artifacts_active"], bool_only=True):
                            continue

                        if self.grabber.search(image=ARTIFACT_MAP.get(art.artifact.name), bool_only=True):
                            self.logger.info("artifact: {artifact} was successfully found, marking as owned".format(
                                artifact=artifact))
                            art.owned = True
                            art.save()

                    except ValueError:
                        self.logger.error("artifact: {artifact} could not be searched for, leaving false".format(
                            artifact=artifact))

            if break_next:
                self.logger.info("artifact: {artifact} was found at the bottom of the screen, exiting parse loop now".format(
                    artifact=self.session.configuration.bottom_artifact))
                break

            # Scroll down slightly and check for artifacts again.
            drag_mouse(start=locs["scroll_start"], end=locs["scroll_bottom_end"], window=self.window, quick_stop=locs["scroll_quick_stop"])
            sleep(1)

            # Checking at the end of the loop to break, one more loop takes place before exit.
            if self.grabber.search(ARTIFACT_MAP.get(self.session.configuration.bottom_artifact.name), region=last_artifact_region, bool_only=True):
                break_next = True

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
            self.logger.debug("ocr result: {key} -> {text}".format(key=key, text=text))

            # The images do not always parse correctly, so we can attempt to parse out our expected
            # value from the STATS_COORD tuple being used.

            # Firstly, confirm that a number is present in the text result, if no numbers are present
            # at all, safe to assume the OCR has failed wonderfully.
            if not any(char.isdigit() for char in text):
                self.logger.warning("no digits found in ocr result, skipping key: {key}".format(key=key))
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

                self.logger.info("parsed value: {key} -> {value}".format(key=key, value=value))
                setattr(self.statistics.game_statistics, key, value)
                self.statistics.game_statistics.save()

            # Gracefully continuing loop if failure occurs.
            except ValueError:
                self.logger.error("could not parse {key}: (ocr result: {text})".format(key=key, text=text))

    def stage_ocr(self, test_image=None):
        """
        Attempt to parse out the current stage in game through an OCR check.
        """
        self.logger.debug("attempting to parse out the current stage from in game")
        region = STAGE_COORDS["region"]

        if test_image:
            image = self._process_stage(scale=3, image=test_image)
        else:
            self.grabber.snapshot(region=region)
            image = self._process_stage(scale=3)

        text = pytesseract.image_to_string(image, config='--psm 7 nobatch digits')
        self.logger.debug("parsed value: {text}".format(text=text))

        # Do some light parse work here to make sure only digit like characters are present
        # in the returned 'text' variable retrieved through tesseract.
        return ''.join(filter(lambda x: x.isdigit(), text))

    def get_advance_start(self, test_image=None):
        """
        Another portion of the functionality that should be used right before a prestige takes place.

        Grab the users advance start value. We can use this to improve the accuracy of our stage parsing
        within the Bot if we know what the users minimum stage value currently is.
        """
        self.logger.info("attempting to parse out the advance start value for current prestige")
        region = PRESTIGE_COORDS["advance_start"]

        if test_image:
            image = self._process_stage(test_image)
        else:
            self.grabber.snapshot(region=region)
            image = self._process_stage()

        text = pytesseract.image_to_string(image, config="--psm 7 nobatch digits")
        self.logger.debug("parsed value: {text}".format(text=text))

        # Doing some light parse work, similar to the stage ocr function to remove letters if present.
        return ''.join(filter(lambda x: x.isdigit(), text))

    def update_prestige(self, artifact, current_stage=None, test_image=None):
        """
        Right before a prestige takes place, we can generate and parse out some information from the screen
        present right before a prestige happens. This panel displays the time since the last prestige, we can store
        this, along with a timestamp for the prestige.

        A final stat can be modified as this is called to determine some overall statistics
        (# of prestige's, average time for prestige, etc)...

        This method expects the current in game panel to be the one right before a prestige takes place.
        """
        self.logger.info("Attempting to parse out the time since last prestige")
        region = PRESTIGE_COORDS["time_since"]

        if test_image:
            image = self._process(scale=3, image=test_image)
        else:
            image = self._process(scale=3, current=True, region=region)

        text = pytesseract.image_to_string(image, config='--psm 7')
        self.logger.info("parsed value: {text}".format(text=text))

        # We now have the amount of time that this prestige took place, appending it to the list of prestiges
        # present in the statistics instance.
        self.logger.info("attempting to parse hours, minutes and seconds from parsed text.")
        try:
            try:
                hours, minutes, seconds = [int(t) for t in text.split(":")]
            except ValueError:
                hours, minutes, seconds = None, None, None

            delta = None
            if hours or minutes or seconds:
                delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

            self.logger.info("generating new prestige instance")
            prestige = Prestige.objects.create(
                timestamp=timezone.now(),
                time=delta,
                stage=current_stage,
                artifact=Artifact.objects.get(
                    name=artifact
                ),
                session=self.session,
                instance=self.instance
            )

            self.logger.info("prestige generated successfully: {prestige}".format(prestige=str(prestige)))
            self.prestige_statistics.prestiges.add(prestige)
            self.prestige_statistics.save()

            # Additionally, we want to attempt to grab the users advanced start value.
            return prestige, self.get_advance_start()

        except Exception as exc:
            self.logger.error("error occurred while creating a prestige instance.")
            self.logger.error(str(exc))

    def clan_name_and_code(self, test_images=None):
        """
        Parse out the current name and code for the users current clan.

        Assuming that the information panel of their clan is currently open.
        """
        self.logger.info("attempting to parse out current clan name and code...")
        region_name = CLAN_COORDS["info_name"]
        region_code = CLAN_COORDS["info_code"]

        if test_images:
            image_name = self._process(test_images[0])
            image_code = self._process(test_images[1])
        else:
            image_name = self._process(current=True, region=region_name)
            image_code = self._process(current=True, region=region_code)

        name = pytesseract.image_to_string(image=image_name, config="--psm 7")
        code = pytesseract.image_to_string(image=image_code, config="--psm 7")

        return name, code

    def get_raid_attacks_reset(self, test_image=None):
        """
        Parse out the current attacks reset value for the current clan raid.

        Assuming that the clan raid panel is currently open.
        """
        self.logger.info("attempting to parse out current clan raid attacks reset...")
        region = CLAN_RAID_COORDS["raid_attack_reset"]

        if test_image:
            image = self._process(test_image)
        else:
            image = self._process(current=True, region=region)

        text = pytesseract.image_to_string(image=image, config="--psm 7")
        self.logger.info("text parsed: {text}".format(text=text))

        delta = delta_from_values(values=text.split(" ")[3:])
        self.logger.info("delta generated: {delta}".format(delta=delta))

        if delta:
            return timezone.now() + delta
        else:
            return None
