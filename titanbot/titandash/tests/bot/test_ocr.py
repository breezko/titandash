"""
test_ocr.py

Test the functionality related to the optical character recognition processes present
in the bot.
"""
from django.conf import settings

from titandash.tests.bot.base import BaseBotTest

from PIL import Image

import os


class TestBotStageOCR(BaseBotTest):
    """
    Test functionality relating to the stage parsing and recognition process.
    """
    @classmethod
    def setUpTestData(cls):
        super(TestBotStageOCR, cls).setUpTestData()

        # Directory containing all of our test images for use
        # with the stage image recognition.
        cls.test_dir = os.path.join(settings.TEST_IMAGE_DIR, "ocr/stage")

        # Creating a list of all our test images, as well as the expected stage
        # text associated with each one.
        cls.test_images = [
            [Image.open(os.path.join(cls.test_dir, "test_stage_01.png")), "12493"],
            [Image.open(os.path.join(cls.test_dir, "test_stage_02.png")), "10651"],
            [Image.open(os.path.join(cls.test_dir, "test_stage_03.png")), "11289"],
            [Image.open(os.path.join(cls.test_dir, "test_stage_04.png")), "10411"],
            [Image.open(os.path.join(cls.test_dir, "test_stage_05.png")), "10920"],
            [Image.open(os.path.join(cls.test_dir, "test_stage_06.png")), "7111"],
            [Image.open(os.path.join(cls.test_dir, "test_stage_07.png")), "9840"],
            [Image.open(os.path.join(cls.test_dir, "test_stage_08.png")), "7284"],
            [Image.open(os.path.join(cls.test_dir, "test_stage_09.png")), "7180"],
        ]

    def test_stage_ocr(self):
        """
        Test that returned stage text is valid.
        """
        for lst in self.test_images:
            self.assertEqual(
                first=self.bot.stats.stage_ocr(test_image=lst[0]),
                second=lst[1]
            )
