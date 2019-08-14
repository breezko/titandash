"""
maps.py

Map any values into a single location useful for determining locations on screen
and mapping the proper values and coordinates to their respective keys.
"""
from settings import IMAGE_DIR

# Some emulators apply some padding or wrapping around their window. This can be accounted for by mapping
# the padding and dealing with it during screenshots.
EMULATOR_PADDING_MAP = {
    "nox": {
        "x": 5,
        "y": 38,
    },
}

EMULATOR_LOCS = {
    "nox": {
        "close_emulator": (469, 17),
        "restart": (296, 472),
    },
}

# All points in game that are relevant to the given resolution can be stored here.
# Not all locations need to be stored here, only locations that otherwise would be
# more of an issue trying to click on after looking for a different image.
GAME_LOCS = {
    "BOTTOM_BAR": {
        "master": (39, 815),
        "heroes": (120, 815),
        "equipment": (200, 815),
        "pets": (281, 815),
        "artifacts": (362, 815),
        "shop": (442, 815),
    },
    "DAILY_REWARD": {
        "open_rewards": (34, 210),
        "close_rewards": (430, 260),
        "collect_rewards": (240, 560),
    },
    "CLAN": {
        "clan": (82, 59),
        "clan_info": (392, 158),
        "clan_info_close": (408, 97),
        "clan_results": (267, 153),
        "clan_results_copy": (80, 262),
        "clan_raid": (109, 750),
    },
    "SKILL_BAR": {
        "heavenly_strike": (43, 744),
        "deadly_strike": (123, 744),
        "hand_of_midas": (200, 744),
        "fire_sword": (283, 744),
        "war_cry": (363, 744),
        "shadow_clone": (444, 744),
    },
    "GAME_SCREEN": {
        "fight_boss": (425, 65),
        "game_middle": (250, 320),
        "player": (235, 421),
        "pet_gold": (287, 411),
        "pet_attack": (235, 377),
        "clan_ship": (60, 188),
        # Start any scroll functions from this point.
        "scroll_start": (328, 530),
        "scroll_top_end": (328, 765),
        "scroll_bottom_end": (328, 80),
        "scroll_quick_stop": (328, 780),
        # The fairies map is looped through and each point is pressed
        # sequentially, this will ensure that fairies are pressed if present.
        "fairies_map": (
            (75, 125), (100, 125), (140, 125), (200, 125), (260, 125), (320, 125), (380, 125), (440, 125),
            (75, 160), (100, 160), (140, 160), (200, 160), (260, 160), (320, 160), (380, 160), (440, 160),
            (75, 230), (100, 230), (140, 230), (200, 230), (260, 230), (320, 230), (380, 230), (440, 230),
            (75, 300), (100, 300), (140, 300), (200, 300), (260, 300), (320, 300), (380, 300), (440, 300),
            (75, 370), (100, 370), (140, 370), (200, 370), (260, 370), (320, 370), (380, 370), (440, 370),
            (75, 440), (100, 440), (140, 440), (200, 440), (260, 440), (320, 440), (380, 440), (440, 440),
            # Click on pet for gold bonus.
            (285, 400),
            # Click on spot where skill points appear.
            (110, 445),
            # Click on spot where equipment appears.
            (355, 445),
        ),
        "clan_crate": (70, 165),
    },
    "PANELS": {
        "expand_collapse_top": (386, 43),
        "expand_collapse_bottom": (386, 478),
        "close_top": (449, 43),
        "close_bottom": (449, 479),
    },
    "TOURNAMENT": {
        "tournament": (30, 105),
        "tournament_prestige": (330, 570),
        "collect_prize": (245, 765),
        "join": (245, 730),
    },
    "EGGS": {
        "hatch_egg": (35, 315),
    },
    "AD": {
        "collect_ad": (365, 650),
        "no_thanks": (135, 650),
    },
    "ARTIFACTS": {
        "bottom_region": (2, 727, 475, 797),
    },
    "EMULATOR": {
        "exit_emulator": (468, 16),
        "restart_emulator": (300, 473),
    },
}

# Points used when clicking on locations present on the master panel.
MASTER_LOCS = {
    "master_level": (415, 170),
    "prestige": (405, 770),
    "prestige_confirm": (245, 660),
    "prestige_final": (330, 570),
    "screen_top": (240, 40),
    "achievements": (207, 537),
    "daily_achievements": (342, 123),
    "skills": {
        "heavenly_strike": (415, 270),
        "deadly_strike": (415, 350),
        "hand_of_midas": (415, 430),
        "fire_sword": (415, 508),
        "war_cry": (415, 580),
        "shadow_clone": (415, 650),
    },
    "skill_level_max": {
        "heavenly_strike": (268, 280),
        "deadly_strike": (268, 357),
        "hand_of_midas": (268, 433),
        "fire_sword": (268, 508),
        "war_cry": (268, 584),
        "shadow_clone": (268, 659),
    },
}

# Points used when clicking on locations present in the heroes panel.
HEROES_LOCS = {
    "drag_heroes": {
        "start": (328, 85),
        # End is quite finicky, be sure to experiment with the y
        # value if using different resolutions.
        "end": (328, 920),
    },
    "level_heroes": (
        (405, 770),
        (405, 690),
        (405, 615),
        (405, 540),
        (405, 465),
        (405, 390),
        (405, 310),
        (405, 240),
        (405, 160),
        (405, 85),
    ),
    "stats_collapsed": (135, 540),
    "stats_expanded": (135, 105),
}

ARTIFACTS_LOCS = {
    # The amount of pixels to push the mouse over when purchasing any artifact. Since the imagesearch
    # will return the top left of the image, we can add these vales to that to click on the purchase button.
    "artifact_push": {
        "x": 401,
        "y": 40,
    },
    "buy_multiplier": (410, 105),
    "buy_max": (50, 105),
    "percent_toggle": (303, 540),
}

# Store any colors used (RGB) by the bot to determine so things in game.
GAME_COLORS = {
    "WHITE": (255, 255, 255)
}

# All images should have their names mapped to the file path within the module.
IMAGES = {
    "ACHIEVEMENTS": {
        "daily_collect": IMAGE_DIR + "/achievements/daily_collect.png",
    },
    "ADS": {
        "collect_ad": IMAGE_DIR + "/ads/collect.png",
        "no_thanks": IMAGE_DIR + "/ads/no_thanks.png",
    },
    "ARTIFACTS": {
        "artifacts_discovered": IMAGE_DIR + "/artifacts/artifacts_discovered.png",
        "book_of_shadows": IMAGE_DIR + "/artifacts/book_of_shadows.png",
        "spend_max": IMAGE_DIR + "/artifacts/spend_max.png",
        "salvaged": IMAGE_DIR + "/artifacts/salvaged.png",
        "percent_on": IMAGE_DIR + "/artifacts/percent_on.png"
    },
    "DAILY_REWARD": {
        "collect_reward": IMAGE_DIR + "/daily_reward/collect.png",
    },
    "EQUIPMENT": {
        "crafting": IMAGE_DIR + "/equipment/crafting.png",
    },
    "GENERIC": {
        "artifacts_active": IMAGE_DIR + "/generic/artifacts_active.png",
        "buy_max": IMAGE_DIR + "/generic/buy_max.png",
        "buy_one": IMAGE_DIR + "/generic/buy_one.png",
        "buy_one_hundred": IMAGE_DIR + "/generic/buy_one_hundred.png",
        "buy_ten": IMAGE_DIR + "/generic/buy_ten.png",
        "collapse_panel": IMAGE_DIR + "/generic/collapse_panel.png",
        "equipment_active": IMAGE_DIR + "/generic/equipment_active.png",
        "exit_panel": IMAGE_DIR + "/generic/exit_panel.png",
        "expand_panel": IMAGE_DIR + "/generic/expand_panel.png",
        "heroes_active": IMAGE_DIR + "/generic/heroes_active.png",
        "large_exit_panel": IMAGE_DIR + "/generic/large_exit_panel.png",
        "master_active": IMAGE_DIR + "/generic/master_active.png",
        "max": IMAGE_DIR + "/generic/max.png",
        "pets_active": IMAGE_DIR + "/generic/pets_active.png",
        "shop_active": IMAGE_DIR + "/generic/shop_active.png",
    },
    "HEROES": {
        "max_level": IMAGE_DIR + "/heroes/max_level.png",
        "maya_muerta": IMAGE_DIR + "/heroes/maya_muerta.png",
        "stats": IMAGE_DIR + "/heroes/stats.png",
        "story": IMAGE_DIR + "/heroes/story.png",
        "masteries": IMAGE_DIR + "/heroes/masteries.png",
    },
    "MASTER": {
        "raid_cards": IMAGE_DIR + "/master/raid_cards.png",
        "achievements": IMAGE_DIR + "/master/achievements.png",
        "cancel_active_skill": IMAGE_DIR + "/master/cancel_active_skill.png",
        "confirm_prestige": IMAGE_DIR + "/master/confirm_prestige.png",
        "deadly_strike": IMAGE_DIR + "/master/deadly_strike.png",
        "fire_sword": IMAGE_DIR + "/master/fire_sword.png",
        "hand_of_midas": IMAGE_DIR + "/master/hand_of_midas.png",
        "heavenly_strike": IMAGE_DIR + "/master/heavenly_strike.png",
        "inbox": IMAGE_DIR + "/master/inbox.png",
        "master": IMAGE_DIR + "/master/master.png",
        "prestige": IMAGE_DIR + "/master/prestige.png",
        "shadow_clone": IMAGE_DIR + "/master/shadow_clone.png",
        "skill_level_zero": IMAGE_DIR + "/master/skill_level_zero.png",
        "skill_max_level": IMAGE_DIR + "/master/skill_max_level.png",
        "skill_tree": IMAGE_DIR + "/master/skill_tree.png",
        "unlock_at": IMAGE_DIR + "/master/unlock_at.png",
        "war_cry": IMAGE_DIR + "/master/war_cry.png",
    },
    "NO_PANELS": {
        "clan_raid_ready": IMAGE_DIR + "/no_panels/clan_raid_ready.png",
        "clan_no_raid": IMAGE_DIR + "/no_panels/clan_no_raid.png",
        "daily_reward": IMAGE_DIR + "/no_panels/daily_reward.png",
        "fight_boss": IMAGE_DIR + "/no_panels/fight_boss.png",
        "hatch_egg": IMAGE_DIR + "/no_panels/hatch_egg.png",
        "leave_boss": IMAGE_DIR + "/no_panels/leave_boss.png",
        "settings": IMAGE_DIR + "/no_panels/clan_battle_ready.png",
        "tournament": IMAGE_DIR + "/no_panels/tournament.png",
    },
    "PETS": {
        "next_egg": IMAGE_DIR + "/pets/next_egg.png",
    },
    "SHOP": {
        "shop_keeper": IMAGE_DIR + "/shop/shop_keeper.png",
    },
    "TOURNAMENT": {
        "join": IMAGE_DIR + "/tournament/join.png",
        "collect_prize": IMAGE_DIR + "/tournament/collect_prize.png",
    },
    "CLAN_CRATE": {
        "okay": IMAGE_DIR + "/clan_crate/okay.png",
    },
    "EMULATOR": {
        "tap_titans_2": IMAGE_DIR + "/emulator/tap_titans_2.png",
        "restart": IMAGE_DIR + "/emulator/restart.png"
    },
    "CLAN": {
        "clan": IMAGE_DIR + "/clan/clan.png",
        "clan_info": IMAGE_DIR + "/clan/clan_info.png",
    },
    "RAID": {
        "raid_fight": IMAGE_DIR + "/raid/raid_fight.png",
    },
    "STATS": {
        "stats_title": IMAGE_DIR + "/stats/stats_title.png",
    }
}

# All coordinates mapped to their respective resolutions for grabbing
# each stat image that will be parsed by pytesseract.
STATS_COORDS = {
    "highest_stage_reached": (55, 474, 430, 495),
    "total_pet_level": (55, 495, 430, 515),
    "gold_earned": (55, 516, 430, 536),
    "taps": (55, 537, 430, 561),
    "titans_killed": (55, 559, 430, 579),
    "bosses_killed": (55, 580, 430, 600),
    "critical_hits": (55, 602, 430, 621),
    "chestersons_killed": (55, 623, 430, 643),
    "prestiges": (55, 645, 430, 666),
    "days_since_install": (55, 670, 430, 686),
    "play_time": (55, 687, 430, 708),
    "relics_earned": (55, 709, 430, 729),
    "fairies_tapped": (55, 731, 430, 751),
    "daily_achievements": (55, 750, 430, 773),
}

STAGE_COORDS = {
    "region": (214, 71, 268, 84),
}

PRESTIGE_COORDS = {
    "time_since": (300, 614, 360, 628),
    "advance_start": (145, 557, 202, 577),
}

# The regions for each skill present on the master screen if the panel
# is expanded and scrolled all the way to the top.
MASTER_COORDS = {
    "skills": {
        "heavenly_strike": (0, 233, 480, 303),
        "deadly_strike": (0, 309, 480, 380),
        "hand_of_midas": (0, 385, 480, 455),
        "fire_sword": (0, 460, 480, 531),
        "war_cry": (0, 536, 480, 607),
        "shadow_clone": (0, 612, 480, 682),
    },
}

CLAN_COORDS = {
    "info_name": (133, 70, 362, 103),
    "info_code": (123, 730, 172, 745),
}

# Clan raid coordinates located in the main clan raid page.
CLAN_RAID_COORDS = {
    "raid_attack_reset": (55, 753, 240, 771),
}

# Set of skills in game.
SKILLS = (
    "heavenly_strike",
    "deadly_strike",
    "hand_of_midas",
    "fire_sword",
    "war_cry",
    "shadow_clone",
)

# Dictionary containing all of the artifacts in game mapped to their respective tier list.
ARTIFACT_TIER_MAP = {
    "S": {
        "book_of_shadows": (IMAGE_DIR + "/artifacts/book_of_shadows.png", 22),
        "stone_of_the_valrunes": (IMAGE_DIR + "/artifacts/stone_of_the_valrunes.png", 2),
        "flute_of_the_soloist": (IMAGE_DIR + "/artifacts/flute_of_the_soloist.png", 84),
        "heart_of_storms": (IMAGE_DIR + "/artifacts/heart_of_storms.png", 52),
        "ring_of_calisto": (IMAGE_DIR + "/artifacts/ring_of_calisto.png", 40),
        "invaders_gjalarhorn": (IMAGE_DIR + "/artifacts/invaders_gjalarhorn.png", 47),
        "boots_of_hermes": (IMAGE_DIR + "/artifacts/boots_of_hermes.png", 70),
    },
    "A": {
        "charged_card": (IMAGE_DIR + "/artifacts/charged_card.png", 95),
        "book_of_prophecy": (IMAGE_DIR + "/artifacts/book_of_prophecy.png", 20),
        "khrysos_bowl": (IMAGE_DIR + "/artifacts/khrysos_bowl.png", 66),
        "the_bronzed_compass": (IMAGE_DIR + "/artifacts/the_bronzed_compass.png", 82),
        "evergrowing_stack": (IMAGE_DIR + "/artifacts/evergrowing_stack.png", 94),
        "heavenly_sword": (IMAGE_DIR + "/artifacts/heavenly_sword.png", 26),
        "divine_retribution": (IMAGE_DIR + "/artifacts/divine_retribution.png", 31),
        "drunken_hammer": (IMAGE_DIR + "/artifacts/drunken_hammer.png", 29),
        "samosek_sword": (IMAGE_DIR + "/artifacts/samosek_sword.png", 51),
        "the_retaliator": (IMAGE_DIR + "/artifacts/the_retaliator.png", 59),
        "stryfe's_peace": (IMAGE_DIR + "/artifacts/stryfes_peace.png", 83),
        "hero's_blade": (IMAGE_DIR + "/artifacts/heros_blade.png", 35),
        "the_sword_of_storms": (IMAGE_DIR + "/artifacts/the_sword_of_storms.png", 32),
        "furies_bow": (IMAGE_DIR + "/artifacts/furies_bow.png", 33),
        "charm_of_the_ancient": (IMAGE_DIR + "/artifacts/charm_of_the_ancient.png", 34),
        "tiny_titan_tree": (IMAGE_DIR + "/artifacts/tiny_titan_tree.png", 61),
        "helm_of_hermes": (IMAGE_DIR + "/artifacts/helm_of_hermes.png", 62),
        "o'ryans_charm": (IMAGE_DIR + "/artifacts/oryans_charm.png", 64),
        "apollo_orb": (IMAGE_DIR + "/artifacts/apollo_orb.png", 53),
        "earrings_of_portara": (IMAGE_DIR + "/artifacts/earrings_of_portara.png", 67),
        "helheim_skull": (IMAGE_DIR + "/artifacts/helheim_skull.png", 56),
        "oath's_burden": (IMAGE_DIR + "/artifacts/oaths_burden.png", 75),
        "crown_of_the_constellation": (IMAGE_DIR + "/artifacts/crown_of_the_constellation.png", 76),
        "titania's_sceptre": (IMAGE_DIR + "/artifacts/titanias_sceptre.png", 77),
        "blade_of_damocles": (IMAGE_DIR + "/artifacts/blade_of_damocles.png", 25),
        "helmet_of_madness": (IMAGE_DIR + "/artifacts/helmet_of_madness.png", 17),
        "titanium_plating": (IMAGE_DIR + "/artifacts/titanium_plating.png", 23),
        "moonlight_bracelet": (IMAGE_DIR + "/artifacts/moonlight_bracelet.png", 73),
        "amethyst_staff": (IMAGE_DIR + "/artifacts/amethyst_staff.png", 28),
        "spearit's_vigil": (IMAGE_DIR + "/artifacts/spearits_vigil.png", 87),
        "sword_of_the_royals": (IMAGE_DIR + "/artifacts/sword_of_the_royals.png", 86),
        "the_cobalt_plate": (IMAGE_DIR + "/artifacts/the_cobalt_plate.png", 88),
        "sigils_of_judgement": (IMAGE_DIR + "/artifacts/sigils_of_judgement.png", 89),
        "foilage_of_the_keeper": (IMAGE_DIR + "/artifacts/foilage_of_the_keeper.png", 90),
        "laborer's_pendant": (IMAGE_DIR + "/artifacts/laborers_pendant.png", 9),
        "bringer_of_ragnarok": (IMAGE_DIR + "/artifacts/bringer_of_ragnarok.png", 10),
        "parchment_of_foresight": (IMAGE_DIR + "/artifacts/parchment_of_foresight.png", 7),
        "unbound_gauntlet": (IMAGE_DIR + "/artifacts/unbound_gauntlet.png", 74),
        "lucky_foot_of_al-mi-raj": (IMAGE_DIR + "/artifacts/lucky_foot_of_al-mi-raj.png", 69),
        "morgelai_sword": (IMAGE_DIR + "/artifacts/morgelai_sword.png", 71),
        "ringing_stone": (IMAGE_DIR + "/artifacts/ringing_stone.png", 91),
        "quill_of_scrolls": (IMAGE_DIR + "/artifacts/quill_of_scrolls.png", 92),
        "old_king's_stamp": (IMAGE_DIR + "/artifacts/old_kings_stamp.png", 93),
        "the_magnifier": (IMAGE_DIR + "/artifacts/the_magnifier.png", 80),
        "the_treasure_of_fergus": (IMAGE_DIR + "/artifacts/the_treasure_of_fergus.png", 81),
        "the_white_dwarf": (IMAGE_DIR + "/artifacts/the_white_dwarf.png", 85),
    },
    "B": {
        "chest_of_contentment": (IMAGE_DIR + "/artifacts/chest_of_contentment.png", 19),
        "heroic_shield": (IMAGE_DIR + "/artifacts/heroic_shield.png", 1),
        "zakynthos_coin": (IMAGE_DIR + "/artifacts/zakynthos_coin.png", 43),
        "great_fay_medallion": (IMAGE_DIR + "/artifacts/great_fay_medallion.png", 44),
        "neko_sculpture": (IMAGE_DIR + "/artifacts/neko_sculpture.png", 45),
        "coins_of_ebizu": (IMAGE_DIR + "/artifacts/coins_of_ebizu.png", 79),
        "fruit_of_eden": (IMAGE_DIR + "/artifacts/fruit_of_eden.png", 38),
        "influential_elixir": (IMAGE_DIR + "/artifacts/influential_elixir.png", 30),
        "avian_feather": (IMAGE_DIR + "/artifacts/avian_feather.png", 42),
        "fagin's_grip": (IMAGE_DIR + "/artifacts/fagins_grip.png", 78),
        "titan's_mask": (IMAGE_DIR + "/artifacts/titans_mask.png", 11),
        "royal_toxin": (IMAGE_DIR + "/artifacts/royal_toxin.png", 41),
        "elixir_of_eden": (IMAGE_DIR + "/artifacts/elixir_of_eden.png", 6),
        "hourglass_of_the_impatient": (IMAGE_DIR + "/artifacts/hourglass_of_the_impatient.png", 65),
        "phantom_timepiece": (IMAGE_DIR + "/artifacts/phantom_timepiece.png", 48),
        "infinity_pendulum": (IMAGE_DIR + "/artifacts/infinity_pendulum.png", 36),
        "glove_of_kuma": (IMAGE_DIR + "/artifacts/glove_of_kuma.png", 27),
        "titan_spear": (IMAGE_DIR + "/artifacts/titan_spear.png", 39),
        "oak_staff": (IMAGE_DIR + "/artifacts/oak_staff.png", 37),
        "the_arcana_cloak": (IMAGE_DIR + "/artifacts/the_arcana_cloak.png", 3),
        "hunter's_ointment": (IMAGE_DIR + "/artifacts/hunters_ointment.png", 8),
        "axe_of_muerte": (IMAGE_DIR + "/artifacts/axe_of_muerte.png", 4),
        "the_master's_sword": (IMAGE_DIR + "/artifacts/the_masters_sword.png", 49),
        "mystical_beans_of_senzu": (IMAGE_DIR + "/artifacts/mystical_beans_of_senzu.png", 68),
    },
    "C": {
        "corrupted_rune_heart": (IMAGE_DIR + "/artifacts/corrupted_rune_heart.png", 46),
        "durendal_sword": (IMAGE_DIR + "/artifacts/durendal_sword.png", 55),
        "forbidden_scroll": (IMAGE_DIR + "/artifacts/forbidden_scroll.png", 13),
        "ring_of_fealty": (IMAGE_DIR + "/artifacts/ring_of_fealty.png", 15),
        "glacial_axe": (IMAGE_DIR + "/artifacts/glacial_axe.png", 16),
        "aegis": (IMAGE_DIR + "/artifacts/aegis.png", 14),
        "swamp_gauntlet": (IMAGE_DIR + "/artifacts/swamp_gauntlet.png", 12),
        "ambrosia_elixir": (IMAGE_DIR + "/artifacts/ambrosia_elixir.png", 50),
        "mystic_staff": (IMAGE_DIR + "/artifacts/mystic_staff.png", 58),
        "egg_of_fortune": (IMAGE_DIR + "/artifacts/egg_of_fortune.png", 18),
        "divine_chalice": (IMAGE_DIR + "/artifacts/divine_chalice.png", 21),
        "invader's_shield": (IMAGE_DIR + "/artifacts/invaders_shield.png", 5),
        "essence_of_kitsune": (IMAGE_DIR + "/artifacts/essence_of_kitsune.png", 54),
        "oberon_pendant": (IMAGE_DIR + "/artifacts/oberon_pendant.png", 72),
        "lost_king's_mask": (IMAGE_DIR + "/artifacts/lost_kings_mask.png", 63),
        "staff_of_radiance": (IMAGE_DIR + "/artifacts/staff_of_radiance.png", 24),
        "aram_spear": (IMAGE_DIR + "/artifacts/aram_spear.png", 57),
        "ward_of_the_darkness": (IMAGE_DIR + "/artifacts/ward_of_the_darkness.png", 60),
    },
}

# Dictionary containing all artifacts in game mapped to their respective image path. No tiers included.
ARTIFACT_MAP = {k1: v1[0] for k, v in ARTIFACT_TIER_MAP.items() for k1, v1 in v.items()}

# Create a set of artifact keys that have a max level (these shouldn't be upgraded). Assuming that
# they are maxed at all times.
ARTIFACT_WITH_MAX_LEVEL = (
    "hourglass_of_the_impatient", "phantom_timepiece", "forbidden_scroll", "ring_of_fealty",
    "glacial_axe", "aegis", "swamp_gauntlet", "infinity_pendulum", "glove_of_kuma", "titan_spear",
    "oak_staff", "the_arcana_cloak", "hunter's_ointment", "ambrosia_elixir", "mystic_staff",
    "mystical_beans_of_senzu", "egg_of_fortune", "divine_chalice", "invader's_shield", "axe_of_muerte",
    "essence_of_the_kitsune", "boots_of_hermes", "unbound_gauntlet", "oberon_pendant",
    "lucky_foot_of_al-mi-raj", "lost_king's_mask", "staff_of_radiance", "morgelai_sword", "ringing_stone",
    "quill_of_scrolls", "old_king's_stamp", "the_master's_sword", "the_magnifier", "the_treasure_of_fergus",
    "the_white_dwarf", "aram_spear", "ward_of_the_darkness",
)
