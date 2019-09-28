"""
grabber.py

Encapsulate the functional class used by the bot to take screenshots of the game screen and search
for specific images present on the screen.
"""
from titandash.bot.external.imagesearch import *


class Grabber:
    """
    Grabber class provides functionality to capture a portion of the screen, based on the height
    and width that the emulator should be set to.
    """
    def __init__(self, window, logger):
        # Base height and width, resolution of game.
        self.window = window
        self.logger = logger

        # Padding provided by emulator, x1, y1.
        self.x = window.x
        self.y = window.y + window.y_padding
        self.width = window.width
        self.height = window.height - window.y_padding

        # x2, y2, represent the width and height of the emulator.
        self.x2 = self.width + self.x
        self.y2 = self.height + self.y

        # Screen is updated and set to the result of an image grab as needed through the snapshot method.
        self.current = None

    def snapshot(self, region=None):
        """
        Take a snapshot of the current game session, based on the width and height of the grabber unless
        an explicit region is specified to use to take a screen-shot with.
        """
        if not region:
            self.logger.debug("taking snapshot of game screen (X1: {x}, Y1: {x}, X2: {x2}, Y2: {y2})".format(
                x=self.x, y=self.y, x2=self.x2, y2=self.y2))
            self.current = region_grabber((self.x, self.y, self.x2, self.y2))
        else:
            self.logger.debug("taking snapshot of region in game screen (X1: {x}, Y1: {y}, X2: {x2}, Y2: {y2}".format(
                x=region[0], y=region[1], x2=region[2], y2=region[3]))

            padded = self.window.y + self.window.y_padding
            region = (
                region[0] + self.window.x, region[1] + padded,
                region[2] + self.window.x, region[3] + padded
            )
            self.current = region_grabber(region)

    def search(self, image, region=None, precision=0.8, bool_only=False, testing=False):
        """
        Search the specified image for another image with a specified amount of precision.

        Specifying bool_only as True will only return whether or not the image is found.

        The testing boolean is used to aid the unit tests to use mock images as a snapshot instead
        of the actual screen.
        """
        if not testing:
            self.logger.debug("searching for {image} in game and returning {bool_or_both}".format(
                image=image, bool_or_both="bool only" if bool_only else "bool and position"))
            self.snapshot()

        found = False
        padded = self.window.y + self.window.y_padding
        try:
            if region:
                region = (
                    region[0] + self.window.x, region[1] + padded,
                    region[2] + self.window.x, region[3] + padded
                )
                position = imagesearcharea(image, region[0], region[1], region[2], region[3], precision)
            else:
                position = imagesearcharea(image, self.x, self.y, self.x2, self.y2, precision, self.current)
        except cv2.error:
            self.logger.error("error occurred during image search, does the file: {file} exist?".format(file=image))
            raise ValueError()

        if position[0] != -1:
            found = True
        if bool_only:
            return found

        # Modify the position to reflect the current window location.
        if position[0] != -1:
            position = (position[0] + self.window.x, position[1] + padded)

        return found, position
