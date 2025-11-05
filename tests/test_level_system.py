"""Tests for dungeon level system."""

import pytest
from roguelike.systems.level_system import (
    DungeonLevel,
    MonsterSpawnRule,
    load_level_config,
)


def test_load_level_config_returns_dict():
    """Loading level config returns a dictionary."""
    levels = load_level_config()
    assert isinstance(levels, dict)


def test_load_level_config_has_five_levels():
    """Level config contains exactly 5 levels."""
    levels = load_level_config()
    assert len(levels) == 5


def test_load_level_config_level_one_exists():
    """Level 1 exists in configuration."""
    levels = load_level_config()
    assert 1 in levels


def test_load_level_config_level_one_is_dungeon_level():
    """Level 1 is a DungeonLevel instance."""
    levels = load_level_config()
    assert isinstance(levels[1], DungeonLevel)


def test_level_one_has_correct_name():
    """Level 1 has name 'Goblin Warren'."""
    levels = load_level_config()
    assert levels[1].name == "Goblin Warren"


def test_level_one_has_correct_dimensions():
    """Level 1 has width 80 and height 50."""
    levels = load_level_config()
    level = levels[1]
    assert level.width == 80 and level.height == 50


def test_level_one_has_correct_room_count():
    """Level 1 has max_rooms set to 30."""
    levels = load_level_config()
    assert levels[1].max_rooms == 30


def test_level_one_has_correct_room_sizes():
    """Level 1 has min_room_size 6 and max_room_size 10."""
    levels = load_level_config()
    level = levels[1]
    assert level.min_room_size == 6 and level.max_room_size == 10


def test_level_one_has_monster_spawn_rules():
    """Level 1 has monster spawn rules dictionary."""
    levels = load_level_config()
    assert isinstance(levels[1].monster_spawn_rules, dict)


def test_level_one_has_orc_spawn_rule():
    """Level 1 has spawn rule for orcs."""
    levels = load_level_config()
    assert "orc" in levels[1].monster_spawn_rules


def test_level_one_orc_spawn_rule_is_correct_type():
    """Level 1 orc spawn rule is MonsterSpawnRule instance."""
    levels = load_level_config()
    assert isinstance(
        levels[1].monster_spawn_rules["orc"], MonsterSpawnRule
    )


def test_level_one_orc_has_base_stats():
    """Level 1 orcs have 1.0 scale for all stats."""
    levels = load_level_config()
    rule = levels[1].monster_spawn_rules["orc"]
    assert (
        rule.hp_scale == 1.0
        and rule.power_scale == 1.0
        and rule.defense_scale == 1.0
    )


def test_level_one_orc_spawn_chance():
    """Level 1 orcs have 0.8 spawn chance."""
    levels = load_level_config()
    assert levels[1].monster_spawn_rules["orc"].chance == 0.8


def test_level_one_has_troll_spawn_rule():
    """Level 1 has spawn rule for trolls."""
    levels = load_level_config()
    assert "troll" in levels[1].monster_spawn_rules


def test_level_five_exists():
    """Level 5 exists in configuration."""
    levels = load_level_config()
    assert 5 in levels


def test_level_five_has_correct_name():
    """Level 5 has name 'Dragon's Sanctum'."""
    levels = load_level_config()
    assert levels[5].name == "Dragon's Sanctum"


def test_level_five_has_more_rooms():
    """Level 5 has more rooms than level 1."""
    levels = load_level_config()
    assert levels[5].max_rooms > levels[1].max_rooms


def test_level_five_orc_stats_scaled():
    """Level 5 orcs have scaled stats higher than 1.0."""
    levels = load_level_config()
    rule = levels[5].monster_spawn_rules["orc"]
    assert rule.hp_scale > 1.0


def test_level_five_has_lower_orc_chance():
    """Level 5 has lower orc spawn chance than level 1."""
    levels = load_level_config()
    assert (
        levels[5].monster_spawn_rules["orc"].chance
        < levels[1].monster_spawn_rules["orc"].chance
    )


def test_level_two_stats_scaled():
    """Level 2 monsters have stats scaled above 1.0."""
    levels = load_level_config()
    rule = levels[2].monster_spawn_rules["orc"]
    assert rule.hp_scale > 1.0 and rule.power_scale > 1.0
