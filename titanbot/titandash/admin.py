from django.contrib import admin
from django.contrib.admin.decorators import register
from django.contrib.auth.models import User, Group

# from .models.token import Token
from .models.artifact import Artifact, Tier
from .models.configuration import Configuration
from .models.bot import BotInstance
from .models.prestige import Prestige
from .models.queue import Queue
from .models.statistics import (
    Statistics, GameStatistics, BotStatistics, ArtifactOwned, ArtifactStatistics,
    PrestigeStatistics, Session
)
from .models.clan import Clan, Member, RaidResult, RaidResultDamage


@register(BotInstance)
class BotInstanceAdmin(admin.ModelAdmin):
    list_display = ["__str__", "state", "started", "session"]


@register(Prestige)
class PrestigeAdmin(admin.ModelAdmin):
    list_display = ["__str__", "timestamp", "stage", "time"]


@register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ["__str__", "created"]


@register(Tier)
class TierAdmin(admin.ModelAdmin):
    pass


@register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ["__str__", "name", "tier", "key", "image"]


@register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    filter_horizontal = ["upgrade_owned_tier", "ignore_artifacts", "upgrade_artifacts"]
    fieldsets = (
        (None, {
            "classes": ("expanded",),
            "fields": ("name",),
        }),
        ("Runtime Settings", {
            "classes": ("expanded",),
            "fields": ("soft_shutdown_on_critical_error", "soft_shutdown_update_stats", "post_action_min_wait_time",
                       "post_action_max_wait_time"),
        }),
        ("Device Settings", {
            "classes": ("expanded",),
            "fields": ("emulator",),
        }),
        ("Generic Settings", {
            "classes": ("expanded",),
            "fields": ("enable_premium_ad_collect", "enable_egg_collection", "enable_tapping", "enable_tournaments",),
        }),
        ("Daily Achievement Settings", {
            "classes": ("expanded",),
            "fields": ("enable_daily_achievements", "daily_achievements_check_on_start", "daily_achievements_check_every_x_hours",),
        }),
        ("Clan Raid Notifications Settings", {
            "classes": ("expanded",),
            "fields": ("enable_raid_notifications", "raid_notifications_check_on_start", "raid_notifications_check_every_x_minutes",
                       "raid_notifications_twilio_account_sid", "raid_notifications_twilio_auth_token", "raid_notifications_twilio_from_number",
                       "raid_notifications_twilio_to_number"),
        }),
        ("Clan Results Parsing Settings", {
            "classes": ("expanded",),
            "fields": ("enable_clan_results_parse", "parse_clan_results_on_start", "parse_clan_results_every_x_minutes",),
        }),
        ("General Action Settings", {
            "classes": ("expanded",),
            "fields": ("run_actions_every_x_seconds", "run_actions_on_start", "order_level_heroes", "order_level_master", "order_level_skills",),
        }),
        ("Master Action Settings", {
            "classes": ("expanded",),
            "fields": ("enable_master", "master_level_intensity",),
        }),
        ("Heroes Action Settings", {
            "classes": ("expanded",),
            "fields": ("enable_heroes", "hero_level_intensity",),
        }),
        ("Skills Action Settings", {
            "classes": ("expanded",),
            "fields": ("enable_skills", "activate_skills_on_start", "interval_heavenly_strike", "interval_deadly_strike",
                       "interval_hand_of_midas", "interval_fire_sword", "interval_war_cry", "interval_shadow_clone",
                       "force_enabled_skills_wait", "max_skill_if_possible", "skill_level_intensity"),
        }),
        ("Prestige Action Settings", {
            "classes": ("expanded",),
            "fields": ("enable_auto_prestige", "prestige_x_minutes", "prestige_at_stage", "prestige_at_max_stage",
                       "prestige_at_max_stage_percent",),
        }),
        ("Artifacts Action Settings", {
            "classes": ("expanded",),
            "fields": ("enable_artifact_purchase", "upgrade_owned_artifacts", "upgrade_owned_tier", "shuffle_artifacts",
                       "ignore_artifacts", "upgrade_artifacts",),
        }),
        ("Stats Settings", {
            "classes": ("expanded",),
            "fields": ("enable_stats", "update_stats_on_start", "update_stats_every_x_minutes",),
        }),
        ("Artifact Parsing Settings", {
            "classes": ("expanded",),
            "fields": ("bottom_artifact",),
        }),
        ("Recovery Settings", {
            "classes": ("expanded",),
            "fields": ("recovery_check_interval_minutes", "recovery_allowed_failures",),
        }),
        ("Logging Settings", {
            "classes": ("expanded",),
            "fields": ("enable_logging", "logging_level",),
        }),
    )


@register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    filter_horizontal = ["sessions"]


@register(GameStatistics)
class GameStatisticsAdmin(admin.ModelAdmin):
    pass


@register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    pass


@register(ArtifactStatistics)
class ArtifactStatisticsAdmin(admin.ModelAdmin):
    filter_horizontal = ["artifacts"]
    pass


@register(ArtifactOwned)
class ArtifactOwnedAdmin(admin.ModelAdmin):
    list_display = ["__str__", "owned"]


@register(PrestigeStatistics)
class PrestigeStatisticsAdmin(admin.ModelAdmin):
    pass


@register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "uuid", "version", "start"]
    pass


@register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display = ["__str__", "name", "code"]


@register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["__str__", "name", "code"]


@register(RaidResultDamage)
class RaidResultDamageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "member", "attacks", "damage"]


@register(RaidResult)
class RaidResultAdmin(admin.ModelAdmin):
    filter_horizontal = ["attacks"]
    list_display = ["__str__", "digest", "parsed", "clan"]
