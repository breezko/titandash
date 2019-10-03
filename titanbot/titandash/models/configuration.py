from django.db import models
from django_paranoid.models import ParanoidModel

from titandash.constants import INFO, LOGGING_LEVEL_CHOICES, EMULATOR_CHOICES


HELP_TEXT = {
    "soft_shutdown_on_critical_error": "Should a soft shutdown be performed if the bot runs into a critical error during a session.",
    "soft_shutdown_update_stats": "Enable stats updates when a soft shutdown is performed.",
    "post_action_min_wait_time": "Determine the minimum amount of seconds to wait after an in game function is finished executing.",
    "post_action_max_wait_time": "Determine the maximum amount of seconds to wait after an in game function is finished executing.",
    "emulator": "Which emulator service is being used?",
    "enable_premium_ad_collect": "Enable the premium ad collection, Note: This will only work if you have unlocked the ability to skip ads, watching ads is not supported.",
    "enable_egg_collection": "Enable the ability to collect and hatch eggs in game.",
    "enable_tapping": "Enable the ability to tap on titans (This also enables the clicking of fairies in game).",
    "enable_tournaments": "Enable the ability to enter and participate in tournaments.",
    "enable_breaks": "Enable the ability to take breaks in game.",
    "breaks_jitter": "Specify a jitter amount so that breaks take place at different intervals.",
    "breaks_minutes_required": "How many minutes of concurrent playtime is required before a break takes place.",
    "breaks_minutes_max": "Maximum amount of minutes to break for.",
    "breaks_minutes_min": "Minimum amount of minutes to break for.",
    "enable_daily_achievements": "Enable the ability to check and collect daily achievements in game.",
    "daily_achievements_check_on_start": "Should daily achievements being checked for when a session is started.",
    "daily_achievements_check_every_x_hours": "Determine how many hours between each daily achievement check.",
    "enable_raid_notifications": "Should notifications be sent to a user when a clan raid starts or attacks are ready.",
    "raid_notifications_check_on_start": "Should a raid notifications check take place when a session is started.",
    "raid_notifications_check_every_x_minutes": "Determine how many minutes between each raid notifications check.",
    "raid_notifications_twilio_account_sid": "Specify the account sid associated with your twilio account.",
    "raid_notifications_twilio_auth_token": "Specify the auth token associated with your twilio account.",
    "raid_notifications_twilio_from_number": "Specify the from number associated with your twilio account",
    "raid_notifications_twilio_to_number": "Specify the phone number you would like to receieve notifications at (ex: +19991234567)",
    "run_actions_every_x_seconds": "Determine how many seconds between each execution of all in game actions.",
    "run_actions_on_start": "Should all actions be executed when a session is started.",
    "order_level_heroes": "Select the order that heroes will be levelled in game (1, 2, 3).",
    "order_level_master": "Select the order that the sword master will be levelled in game (1, 2, 3).",
    "order_level_skills": "Select the order that skills will be levelled in game (1, 2, 3).",
    "enable_master": "Enable the ability to level the sword master in game.",
    "master_level_intensity": "Determine the amount of clicks performed whenever the sword master is levelled.",
    "enable_heroes": "Enable the ability level heroes in game.",
    "hero_level_intensity": "Determine the amount of clicks performed on each hero when they are levelled.",
    "enable_skills": "Enable the ability to level and activate skills in game.",
    "activate_skills_on_start": "Should skills be activated when a session is started.",
    "interval_heavenly_strike": "How many seconds between each activation of the heavenly strike skill.",
    "interval_deadly_strike": "How many seconds between each activation of the deadly strike skill.",
    "interval_hand_of_midas": "How many seconds between each activation of the hand of midas skill.",
    "interval_fire_sword": "How many seconds between each activation of the fire sword skill.",
    "interval_war_cry": "How many seconds between each activation of the war cry skill.",
    "interval_shadow_clone": "How many seconds between each activation of the shadow clone skill.",
    "force_enabled_skills_wait": "Based on the intervals determined above, should skill activation wait until the largest interval is surpassed.",
    "max_skill_if_possible": "Should a skill be levelled to it's maximum available amount if the option is present when a single level is bought.",
    "skill_level_intensity": "Determine the amount of clicks performed on each skill when levelled.",
    "enable_auto_prestige": "Enable the ability to automatically prestige in game.",
    "prestige_x_minutes": "Determine the amount of minutes between each auto prestige process. This can be used for farming, or as a hard limit that is used if the thresholds below aren't met within this time. (0 = off).",
    "prestige_at_stage": "Determine the stage needed before the prestige process is started (Once you reach/pass this stage, you will prestige). (0 = off).",
    "prestige_at_max_stage": "Should a prestige take place once your max stage has been reached? (Stats must be up to date).",
    "prestige_at_max_stage_percent": "Determine if you would like to perform an automatic prestige once a certain percent of your max stage has been reached. You may use values larger than 100 here to push your max stage. (0 = off).",
    "enable_artifact_purchase": "Enable the ability to purchase artifacts in game after a prestige has taken place.",
    "enable_artifact_discover_enchant": "Enable the ability to discover or enchant artifacts if possible after a prestige.",
    "upgrade_owned_tier": "Upgrade a specific tier (or tiers) of artifacts only.",
    "shuffle_artifacts": "Should owned artifacts be shuffled once calculated.",
    "ignore_artifacts": "Should any specific artifacts be ignored regardless of them being owned or not.",
    "upgrade_artifacts": "Should any artifacts be specifically upgraded, disabling the above settings and choosing an artifact here will only upgrade this artifact.",
    "enable_stats": "Enable the ability to update statistics during game sessions.",
    "update_stats_on_start": "Should stats be updated when a session is started.",
    "update_stats_every_x_minutes": "Determine how many minutes between each stats update in game.",
    "enable_clan_results_parse": "Enable the ability to have the bot attempt to parse out clan raid results.",
    "parse_clan_results_on_start": "Should clan results be parsed when a session is started.",
    "parse_clan_results_every_x_minutes": "Determine how many minutes between each clan results parse attempt.",
    "bottom_artifact": "Specify which artifact is currently at the bottom of the artifact list. This is used to determine when to full stop during artifact parsing.",
    "recovery_check_interval_minutes": "Determine how many minutes between each check that determines if the game has crashed/broke.",
    "recovery_allowed_failures": "How many failures are allowed before the recovery process is started.",
    "enable_logging": "Enable logging of information during sessions.",
    "logging_level": "Determine the logging level used during sessions."
}


class Configuration(ParanoidModel):
    """
    Configuration Model.

    Store set of configuration values here. These may be used by a user when starting a bot session.
    Multiple can be created and swapped out as needed.
    """
    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"

    name = models.CharField(max_length=255)

    # RUNTIME Settings.
    soft_shutdown_on_critical_error = models.BooleanField(verbose_name="Soft Shutdown On Critical Error", default=False, help_text=HELP_TEXT["soft_shutdown_on_critical_error"])
    soft_shutdown_update_stats = models.BooleanField(verbose_name="Update Stats On Soft Shutdown", default=True, help_text=HELP_TEXT["soft_shutdown_update_stats"])
    post_action_min_wait_time = models.PositiveIntegerField(verbose_name="Post Action Min Wait Time", default=0, help_text=HELP_TEXT["post_action_min_wait_time"])
    post_action_max_wait_time = models.PositiveIntegerField(verbose_name="Post Action Max Wait Time", default=1, help_text=HELP_TEXT["post_action_max_wait_time"])

    # DEVICE Settings.
    emulator = models.CharField(verbose_name="Emulator", choices=EMULATOR_CHOICES, default=EMULATOR_CHOICES[0][0], max_length=255, help_text=HELP_TEXT["emulator"])

    # GENERIC Settings.
    enable_premium_ad_collect = models.BooleanField(verbose_name="Enable Premium Ad Collection", default=True, help_text=HELP_TEXT["enable_premium_ad_collect"])
    enable_egg_collection = models.BooleanField(verbose_name="Enable Egg Collection", default=True, help_text=HELP_TEXT["enable_egg_collection"])
    enable_tapping = models.BooleanField(verbose_name="Enable Tapping", default=True, help_text=HELP_TEXT["enable_tapping"])
    enable_tournaments = models.BooleanField(verbose_name="Enable Tournaments", default=True, help_text=HELP_TEXT["enable_tournaments"])

    # BREAKS Settings.
    enable_breaks = models.BooleanField(verbose_name="Enable Breaks", default=True, help_text=HELP_TEXT["enable_breaks"])
    breaks_jitter = models.PositiveIntegerField(verbose_name="Breaks Jitter Amount", default=40, help_text=HELP_TEXT["breaks_jitter"])
    breaks_minutes_required = models.PositiveIntegerField(verbose_name="Minutes Required Before Break Is Activated", default=180, help_text=HELP_TEXT["breaks_minutes_required"])
    breaks_minutes_max = models.PositiveIntegerField(verbose_name="Max Minutes For Break", default=60, help_text=HELP_TEXT["breaks_minutes_max"])
    breaks_minutes_min = models.PositiveIntegerField(verbose_name="Min Minutes For Break", default=20, help_text=HELP_TEXT["breaks_minutes_min"])

    # DAILY ACHIEVEMENT Settings.
    enable_daily_achievements = models.BooleanField(verbose_name="Enable Daily Achievements", default=True, help_text=HELP_TEXT["enable_daily_achievements"])
    daily_achievements_check_on_start = models.BooleanField(verbose_name="Check Daily Achievements On Session Start", default=False, help_text=HELP_TEXT["daily_achievements_check_on_start"])
    daily_achievements_check_every_x_hours = models.PositiveIntegerField(verbose_name="Check Daily Achievements Every X Hours", default=1, help_text=HELP_TEXT["daily_achievements_check_every_x_hours"])

    # RAID NOTIFICATION Settings.
    enable_raid_notifications = models.BooleanField(verbose_name="Enable Raid Notifications", default=False, help_text=HELP_TEXT["enable_raid_notifications"])
    raid_notifications_check_on_start = models.BooleanField(verbose_name="Check For Raid Notification On Session Start", default=False, help_text=HELP_TEXT["raid_notifications_check_on_start"])
    raid_notifications_check_every_x_minutes = models.PositiveIntegerField(verbose_name="Check For Raid Notification Every X Minutes", default=30, help_text=HELP_TEXT["raid_notifications_check_every_x_minutes"])

    raid_notifications_twilio_account_sid = models.CharField(verbose_name="Raid Notifications Twilio Account SID", blank=True, null=True, max_length=255, help_text=HELP_TEXT["raid_notifications_twilio_account_sid"])
    raid_notifications_twilio_auth_token = models.CharField(verbose_name="Raid Notifications Twilio Auth Token", blank=True, null=True, max_length=255, help_text=HELP_TEXT["raid_notifications_twilio_auth_token"])
    raid_notifications_twilio_from_number = models.CharField(verbose_name="Raid Notifications Twilio From Number", blank=True, null=True, max_length=255, help_text=HELP_TEXT["raid_notifications_twilio_from_number"])
    raid_notifications_twilio_to_number = models.CharField(verbose_name="Raid Notifications Twilio To Number", blank=True, null=True, max_length=255, help_text=HELP_TEXT["raid_notifications_twilio_to_number"])

    # GENERAL ACTION Settings.
    run_actions_every_x_seconds = models.PositiveIntegerField(verbose_name="Run Actions Every X Seconds", default=25, help_text=HELP_TEXT["run_actions_every_x_seconds"])
    run_actions_on_start = models.BooleanField(verbose_name="Run Actions On Session Start", default=False, help_text=HELP_TEXT["run_actions_on_start"])
    order_level_heroes = models.PositiveIntegerField(choices=((1, "1",), (2, "2",), (3, "3")), default=1, help_text=HELP_TEXT["order_level_heroes"])
    order_level_master = models.PositiveIntegerField(choices=((1, "1",), (2, "2",), (3, "3")), default=2, help_text=HELP_TEXT["order_level_master"])
    order_level_skills = models.PositiveIntegerField(choices=((1, "1",), (2, "2",), (3, "3")), default=3, help_text=HELP_TEXT["order_level_skills"])

    # MASTER ACTION Settings.
    enable_master = models.BooleanField(verbose_name="Enable Master", default=True, help_text=HELP_TEXT["enable_master"])
    master_level_intensity = models.PositiveIntegerField(verbose_name="Master Level Intensity", default=5, help_text=HELP_TEXT["master_level_intensity"])

    # HEROES ACTION Settings.
    enable_heroes = models.BooleanField(verbose_name="Enable Heroes", default=True, help_text=HELP_TEXT["enable_heroes"])
    hero_level_intensity = models.PositiveIntegerField(verbose_name="Hero Level Intensity", default=3, help_text=HELP_TEXT["hero_level_intensity"])

    # SKILLS ACTION Settings.
    enable_skills = models.BooleanField(verbose_name="Enable Skills", default=True, help_text=HELP_TEXT["enable_skills"])
    activate_skills_on_start = models.BooleanField(verbose_name="Activate Skills On Session Start", default=True, help_text=HELP_TEXT["activate_skills_on_start"])
    interval_heavenly_strike = models.PositiveIntegerField(verbose_name="Heavenly Strike Interval", default=0, help_text=HELP_TEXT["interval_heavenly_strike"])
    interval_deadly_strike = models.PositiveIntegerField(verbose_name="Deadly Strike Interval", default=20, help_text=HELP_TEXT["interval_deadly_strike"])
    interval_hand_of_midas = models.PositiveIntegerField(verbose_name="Hand Of Midas Interval", default=30, help_text=HELP_TEXT["interval_hand_of_midas"])
    interval_fire_sword = models.PositiveIntegerField(verbose_name="Fire Sword Interval", default=40, help_text=HELP_TEXT["interval_fire_sword"])
    interval_war_cry = models.PositiveIntegerField(verbose_name="War Cry Interval", default=50, help_text=HELP_TEXT["interval_war_cry"])
    interval_shadow_clone = models.PositiveIntegerField(verbose_name="Shadow Clone Interval", default=60, help_text=HELP_TEXT["interval_shadow_clone"])
    force_enabled_skills_wait = models.BooleanField(verbose_name="Force Enabled Skills Wait", default=False, help_text=HELP_TEXT["force_enabled_skills_wait"])
    max_skill_if_possible = models.BooleanField(verbose_name="Max Skill If Possible", default=True, help_text=HELP_TEXT["max_skill_if_possible"])
    skill_level_intensity = models.PositiveIntegerField(verbose_name="Skill Level Intensity", default=10, help_text=HELP_TEXT["skill_level_intensity"])

    # PRESTIGE ACTION Settings.
    enable_auto_prestige = models.BooleanField(verbose_name="Enable Auto Prestige", default=True, help_text=HELP_TEXT["enable_auto_prestige"])
    prestige_x_minutes = models.PositiveIntegerField(verbose_name="Prestige In X Minutes", default=45, help_text=HELP_TEXT["prestige_x_minutes"])
    prestige_at_stage = models.PositiveIntegerField(verbose_name="Prestige At Stage", default=0, help_text=HELP_TEXT["prestige_at_stage"])
    prestige_at_max_stage = models.BooleanField(verbose_name="Prestige At Max Stage", default=False, help_text=HELP_TEXT["prestige_at_max_stage"])
    prestige_at_max_stage_percent = models.DecimalField(verbose_name="Prestige At Max Stage Percent", default=0, decimal_places=3, max_digits=255, help_text=HELP_TEXT["prestige_at_max_stage_percent"])

    # ARTIFACTS ACTION Settings.
    enable_artifact_discover_enchant = models.BooleanField(verbose_name="Enable Artifact Discover/Enchant", default=True, help_text=HELP_TEXT["enable_artifact_discover_enchant"])
    enable_artifact_purchase = models.BooleanField(verbose_name="Enable Artifact Purchase", default=True, help_text=HELP_TEXT["enable_artifact_purchase"])
    upgrade_owned_tier = models.ManyToManyField(verbose_name="Upgrade Owned Tier", to="Tier", blank=True, related_name='upgrade_tiers', help_text=HELP_TEXT["upgrade_owned_tier"])
    shuffle_artifacts = models.BooleanField(verbose_name="Shuffle Artifacts", default=True, help_text=HELP_TEXT["shuffle_artifacts"])
    ignore_artifacts = models.ManyToManyField(verbose_name="Ignore Artifacts", to="Artifact", blank=True, related_name='ignore_artifacts', help_text=HELP_TEXT["ignore_artifacts"])
    upgrade_artifacts = models.ManyToManyField(verbose_name="Upgrade Artifacts", to="Artifact", blank=True, related_name='upgrade_artifacts', help_text=HELP_TEXT["upgrade_artifacts"])

    # STATS Settings.
    enable_stats = models.BooleanField(verbose_name="Enable Stats", default=True, help_text=HELP_TEXT["enable_stats"])
    update_stats_on_start = models.BooleanField(verbose_name="Update Stats On Session Start", default=False, help_text=HELP_TEXT["update_stats_on_start"])
    update_stats_every_x_minutes = models.PositiveIntegerField(verbose_name="Update Stats Every X Minutes", default=60, help_text=HELP_TEXT["update_stats_every_x_minutes"])

    # RAID PARSING Settings.
    enable_clan_results_parse = models.BooleanField(verbose_name="Enable Clan Results Parsing", default=True, help_text=HELP_TEXT["enable_clan_results_parse"])
    parse_clan_results_on_start = models.BooleanField(verbose_name="Parse Clan Results On Session Start", default=False, help_text=HELP_TEXT["parse_clan_results_on_start"])
    parse_clan_results_every_x_minutes = models.PositiveIntegerField(verbose_name="Attempt To Parse Clan Results Every X Minutes", default=300, help_text=HELP_TEXT["parse_clan_results_every_x_minutes"])

    # ARTIFACT PARSING Settings.
    bottom_artifact = models.ForeignKey(verbose_name="Bottom Artifact", to="Artifact", related_name='bottom_artifact', on_delete=models.CASCADE, help_text=HELP_TEXT["bottom_artifact"])

    # RECOVERY Settings.
    recovery_check_interval_minutes = models.PositiveIntegerField(verbose_name="Recovery Check Interval Minutes", default=5, help_text=HELP_TEXT["recovery_check_interval_minutes"])
    recovery_allowed_failures = models.PositiveIntegerField(verbose_name="Recovery Allowed Failures", default=45, help_text=HELP_TEXT["recovery_allowed_failures"])

    # LOGGING Settings.
    enable_logging = models.BooleanField(verbose_name="Enable Logging", default=True, help_text=HELP_TEXT["enable_logging"])
    logging_level = models.CharField(verbose_name="Logging Level", choices=LOGGING_LEVEL_CHOICES, default=INFO, max_length=255, help_text=HELP_TEXT["logging_level"])

    def __str__(self):
        return "{name}".format(name=self.name)

    def json(self, condense=False):
        """
        Return a JSON compliant dictionary for current configuration.

        Use the condense flag to ensure that foreign key or many to many fields are condensed into simple values.
        """
        from titandash.utils import title
        dct = {
            # RUNTIME.
            "Runtime": {
                "name": self.name,
                "soft_shutdown_on_critical_error": self.soft_shutdown_on_critical_error,
                "soft_shutdown_update_stats": self.soft_shutdown_update_stats,
                "post_action_min_wait_time": self.post_action_min_wait_time,
                "post_action_max_wait_time": self.post_action_max_wait_time
            },
            "Device": {
                "emulator": self.emulator
            },
            "Generic": {
                "enable_premium_ad_collect": self.enable_premium_ad_collect,
                "enable_egg_collection": self.enable_egg_collection,
                "enable_tapping": self.enable_tapping,
                "enable_tournaments": self.enable_tournaments
            },
            "Breaks": {
                "enable_breaks": self.enable_breaks,
                "breaks_jitter": self.breaks_jitter,
                "breaks_minutes_required": self.breaks_minutes_required,
                "breaks_minutes_max": self.breaks_minutes_max,
                "breaks_minutes_min": self.breaks_minutes_min
            },
            "Daily Achievement": {
                "enable_daily_achievements": self.enable_daily_achievements,
                "daily_achievements_check_on_start": self.daily_achievements_check_on_start,
                "daily_achievements_check_every_x_hours": self.daily_achievements_check_every_x_hours
            },
            "Raid Notifications": {
                "enable_raid_notifications": self.enable_raid_notifications,
                "raid_notifications_check_on_start": self.raid_notifications_check_on_start,
                "raid_notifications_check_every_x_minutes": self.raid_notifications_check_every_x_minutes,
                "raid_notifications_twilio_account_sid": self.raid_notifications_twilio_account_sid,
                "raid_notifications_twilio_auth_token": self.raid_notifications_twilio_auth_token,
                "raid_notifications_twilio_from_number": self.raid_notifications_twilio_from_number,
                "raid_notifications_twilio_to_number": self.raid_notifications_twilio_to_number
            },
            "General Actions": {
                "run_actions_every_x_seconds": self.run_actions_every_x_seconds,
                "run_actions_on_start": self.run_actions_on_start,
                "order_level_heroes": self.order_level_heroes,
                "order_level_master": self.order_level_master,
                "order_level_skills": self.order_level_skills
            },
            "Master Actions": {
                "enable_master": self.enable_master,
                "master_level_intensity": self.master_level_intensity
            },
            "Heroes": {
                "enable_heroes": self.enable_heroes,
                "hero_level_intensity": self.hero_level_intensity
            },
            "Skills": {
                "enable_skills": self.enable_skills,
                "activate_skills_on_start": self.activate_skills_on_start,
                "interval_heavenly_strike": self.interval_heavenly_strike,
                "interval_deadly_strike": self.interval_deadly_strike,
                "interval_hand_of_midas": self.interval_hand_of_midas,
                "interval_fire_sword": self.interval_fire_sword,
                "interval_war_cry": self.interval_war_cry,
                "interval_shadow_clone": self.interval_shadow_clone,
                "force_enabled_skills_wait": self.force_enabled_skills_wait,
                "max_skill_if_possible": self.max_skill_if_possible,
                "skill_level_intensity": self.skill_level_intensity
            },
            "Prestige Action": {
                "enable_auto_prestige": self.enable_auto_prestige,
                "prestige_x_minutes": self.prestige_x_minutes,
                "prestige_at_stage": self.prestige_at_stage,
                "prestige_at_max_stage": self.prestige_at_max_stage,
                "prestige_at_max_stage_percent": self.prestige_at_max_stage_percent
            },
            "Artifacts Action": {
                "enable_artifact_purchase": self.enable_artifact_purchase,
                "upgrade_owned_tier": [tier.json() for tier in self.upgrade_owned_tier.all()],
                "shuffle_artifacts": self.shuffle_artifacts,
                "ignore_artifacts": [art.json() for art in self.ignore_artifacts.all()],
                "upgrade_artifacts": [art.json() for art in self.upgrade_artifacts.all()]
            },
            "Stats": {
                "enable_stats": self.enable_stats,
                "update_stats_on_start": self.update_stats_on_start,
                "update_stats_every_x_minutes": self.update_stats_every_x_minutes
            },
            "Raid Parsing": {
                "enable_clan_results_parse": self.enable_clan_results_parse,
                "parse_clan_results_on_start": self.parse_clan_results_on_start,
                "parse_clan_results_every_x_minutes": self.parse_clan_results_every_x_minutes
            },
            "Artifacts": {
                "bottom_artifact": self.bottom_artifact.json()
            },
            "Recovery": {
                "recovery_check_interval_minutes": self.recovery_check_interval_minutes,
                "recovery_allowed_failures": self.recovery_allowed_failures
            },
            "Logging": {
                "enable_logging": self.enable_logging,
                "logging_level": self.logging_level
            }
        }

        if condense:
            dct["Artifacts Action"]["upgrade_owned_tier"] = ", ".join([title(t.name) for t in self.upgrade_owned_tier.all()])
            dct["Artifacts Action"]["ignore_artifacts"] = ", ".join([title(a.name) for a in self.ignore_artifacts.all()])
            dct["Artifacts Action"]["upgrade_artifacts"] = ", ".join([title(a.name) for a in self.upgrade_artifacts.all()])
            dct["Artifacts"]["bottom_artifact"] = title(self.bottom_artifact.name)

        return dct


THEME_CONFIG_HELP_TEXT = {
    "theme": "Determine the name of the theme that will be activated on the dashboard."
}


class ThemeConfigManager(models.Manager):
    """
    Attempt to grab the current theme config instance. We only ever want one single instance. If one does not exist,
    we generate a new one with some default values.
    """
    def grab(self):
        if len(self.all()) == 0:
            self.create()

        # Returning the existing instance.
        return self.all().first()


class ThemeConfig(models.Model):
    """
    ThemeConfig Model.

    Use this model to store the currently selected theme used within the dashboard.
    """
    class Meta:
        verbose_name = "Theme Config"
        verbose_name_plural = "Theme Config's"

    objects = ThemeConfigManager()
    theme = models.CharField(verbose_name="Theme", default="default", max_length=255, help_text=THEME_CONFIG_HELP_TEXT["theme"])
