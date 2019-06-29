"""
test_bot.py

Test the functionality related to the Bot that does not require any interaction between the
in game screen. Utility type functions present may be tested here.
"""
from titandash.tests.bot.base import BaseBotTest
from titandash.models.artifact import Artifact, Tier
from titandash.bot.core.maps import ARTIFACT_WITH_MAX_LEVEL


class TestBotArtifacts(BaseBotTest):
    """Test functionality related to artifact usage within the Bot."""
    @classmethod
    def setUpTestData(cls):
        """Configure expected tiers and artifacts."""
        super(TestBotArtifacts, cls).setUpTestData()

        cls.s_tier = Tier.objects.get(tier="S")
        cls.a_tier = Tier.objects.get(tier="A")
        cls.b_tier = Tier.objects.get(tier="B")
        cls.c_tier = Tier.objects.get(tier="C")

        cls.s_arts = Artifact.objects.tier(tier=cls.s_tier.tier, as_list=True, ignore=ARTIFACT_WITH_MAX_LEVEL)
        cls.a_arts = Artifact.objects.tier(tier=cls.a_tier.tier, as_list=True, ignore=ARTIFACT_WITH_MAX_LEVEL)
        cls.b_arts = Artifact.objects.tier(tier=cls.b_tier.tier, as_list=True, ignore=ARTIFACT_WITH_MAX_LEVEL)
        cls.c_arts = Artifact.objects.tier(tier=cls.c_tier.tier, as_list=True, ignore=ARTIFACT_WITH_MAX_LEVEL)

        # Combine all tiers/artifacts for use where needed.
        cls.all_tiers = [cls.s_tier] + [cls.a_tier] + [cls.b_tier] + [cls.c_tier]
        cls.all_arts = cls.s_arts | cls.a_arts | cls.b_arts | cls.c_arts

    def setUp(self):
        self.bot.configuration.upgrade_owned_tier.clear()

    def _test_artifact_tier(self, tier, expected):
        self.bot.configuration.upgrade_owned_tier.clear()

        if isinstance(tier, Tier):
            self.bot.configuration.upgrade_owned_tier.add(tier)
        else:
            self.bot.configuration.upgrade_owned_tier.add(*tier)

        # Grab all artifacts for the specified configuration tier.
        # Testing boolean ensures that owned artifacts are irrelevant.
        # Assuming all artifacts are owned.
        artifacts = self.bot.get_upgrade_artifacts(testing=True)

        # Calculated artifacts == expected.
        self.assertEqual(len(artifacts), len(expected))

        for artifact in self.bot.get_upgrade_artifacts(testing=True):
            self.assertTrue(artifact in expected)

    def test_tiers(self):
        """Test that modifying upgrade owned tier selections modifies artifacts that will be upgraded."""
        # Test S Tier Artifacts.
        self._test_artifact_tier(self.s_tier, self.s_arts)
        # Test A Tier Artifacts.
        self._test_artifact_tier(self.a_tier, self.a_arts)
        # Test B Tier Artifacts.
        self._test_artifact_tier(self.b_tier, self.b_arts)
        # Test C Tier Artifacts.
        self._test_artifact_tier(self.c_tier, self.c_arts)
        # Test All Tier Artifacts.
        self._test_artifact_tier(self.all_tiers, self.all_arts)

    def test_ignore_artifacts(self):
        """Test that ignoring artifacts works properly."""
        # Grab the Artifact instances that we will be ignoring.
        ignore = Artifact.objects.filter(name__in=["book_of_shadows", "flute_of_the_soloist"])
        expect = Artifact.objects.tier(tier=self.s_tier.tier, ignore=ARTIFACT_WITH_MAX_LEVEL)
        expect = expect.exclude(name__in=ignore.values("name")).values_list("name", flat=True)

        self.bot.configuration.upgrade_owned_tier.add(self.s_tier)
        self.bot.configuration.ignore_artifacts.add(*ignore)

        # Grab artifacts after modifying the ignore artifacts to ensure certain artifacts
        # are ignored and not upgraded.
        artifacts = self.bot.get_upgrade_artifacts(testing=True)
        self.assertEqual(len(artifacts), len(expect))
        for artifact in artifacts:
            self.assertTrue(artifact in expect)

    def test_specific_artifacts(self):
        """Test that upgrading specific artifacts works properly."""
        # Grab the Artifact instances we will be upgrading.
        upgrade = Artifact.objects.filter(name__in=["charged_card", "evergrowing_stack"])
        expect = Artifact.objects.tier(tier=self.s_tier.tier, ignore=ARTIFACT_WITH_MAX_LEVEL) | upgrade
        expect = expect.values_list("name", flat=True)

        self.bot.configuration.upgrade_owned_tier.add(self.s_tier)
        self.bot.configuration.upgrade_artifacts.add(*upgrade)

        # Grab artifacts after modifying the upgrade artifacts to ensure certain artifacts
        # are included as upgrade artifacts.
        artifacts = self.bot.get_upgrade_artifacts(testing=True)
        self.assertEqual(len(artifacts), len(expect))
        for artifact in artifacts:
            self.assertTrue(artifact in expect)

    def test_next_artifact_upgrade(self):
        """Test that the next artifact upgrade iteration works as intended."""
        self.bot.configuration.upgrade_owned_tier.add(self.s_tier)
        self.bot.configuration.shuffle_artifacts = False

        # Retrieve artifacts that should be upgraded.
        artifacts = self.bot.get_upgrade_artifacts(testing=True)

        # Modify bot values.
        self.bot.owned_artifacts = artifacts
        self.bot.next_artifact_index = 0

        self.assertEqual(self.bot.next_artifact_upgrade, None)

        # Loop through owned artifacts, check that update to next artifact
        # is iterating through list properly.
        check = 0
        for i in range(20):
            if check % len(artifacts) == 0:
                check = 0

            self.bot.update_next_artifact_upgrade()
            self.assertEqual(artifacts[check], self.bot.next_artifact_upgrade)

            # Check bumped by one each time...
            check += 1
