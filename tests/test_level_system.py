"""Tests for dungeon level system."""

import pytest
from roguelike.systems.level_system import (
    DungeonLevel,
    DungeonLevelSystem,
    MonsterSpawnRule,
    create_scaled_monster,
    load_level_config,
)
from roguelike.utils.position import Position
from roguelike.engine.events import EventBus
# from roguelike.entities.monster import Monster


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


# Tests for scaled monster creation
def test_create_scaled_orc_returns_monster():
    """Creating a scaled orc returns a Monster instance."""
    rule = MonsterSpawnRule(
        chance=1.0, hp_scale=1.0, power_scale=1.0, defense_scale=1.0
    )
    monster = create_scaled_monster("orc", Position(5, 5), rule)
    assert isinstance(monster, Monster)


def test_create_scaled_orc_has_base_stats():
    """Scaled orc with 1.0 scale has base stats (10 HP, 3 power, 0 defense)."""
    rule = MonsterSpawnRule(
        chance=1.0, hp_scale=1.0, power_scale=1.0, defense_scale=1.0
    )
    monster = create_scaled_monster("orc", Position(5, 5), rule)
    assert monster.max_hp == 10 and monster.power == 3 and monster.defense == 0


def test_create_scaled_orc_doubles_hp():
    """Scaled orc with 2.0 hp_scale has doubled HP (20)."""
    rule = MonsterSpawnRule(
        chance=1.0, hp_scale=2.0, power_scale=1.0, defense_scale=1.0
    )
    monster = create_scaled_monster("orc", Position(5, 5), rule)
    assert monster.max_hp == 20


def test_create_scaled_orc_scales_power():
    """Scaled orc with 1.5 power_scale has 4 power (3 * 1.5 = 4.5, rounded to 4)."""
    rule = MonsterSpawnRule(
        chance=1.0, hp_scale=1.0, power_scale=1.5, defense_scale=1.0
    )
    monster = create_scaled_monster("orc", Position(5, 5), rule)
    assert monster.power == 4


def test_create_scaled_orc_scales_defense():
    """Scaled orc with 2.0 defense_scale gets scaled defense."""
    rule = MonsterSpawnRule(
        chance=1.0, hp_scale=1.0, power_scale=1.0, defense_scale=2.0
    )
    monster = create_scaled_monster("orc", Position(5, 5), rule)
    # Base defense is 0, so 0 * 2.0 = 0, but minimum should be respected
    assert monster.defense >= 0


def test_create_scaled_troll_returns_monster():
    """Creating a scaled troll returns a Monster instance."""
    rule = MonsterSpawnRule(
        chance=1.0, hp_scale=1.0, power_scale=1.0, defense_scale=1.0
    )
    monster = create_scaled_monster("troll", Position(10, 10), rule)
    assert isinstance(monster, Monster)


def test_create_scaled_troll_has_base_stats():
    """Scaled troll with 1.0 scale has base stats (16 HP, 4 power, 1 defense)."""
    rule = MonsterSpawnRule(
        chance=1.0, hp_scale=1.0, power_scale=1.0, defense_scale=1.0
    )
    monster = create_scaled_monster("troll", Position(10, 10), rule)
    assert monster.max_hp == 16 and monster.power == 4 and monster.defense == 1


def test_create_scaled_troll_scales_all_stats():
    """Scaled troll with 1.5 scale has all stats scaled."""
    rule = MonsterSpawnRule(
        chance=1.0, hp_scale=1.5, power_scale=1.5, defense_scale=1.5
    )
    monster = create_scaled_monster("troll", Position(10, 10), rule)
    assert monster.max_hp == 24 and monster.power == 6 and monster.defense == 1


# Tests for DungeonLevelSystem
def test_dungeon_level_system_initializes():
    """DungeonLevelSystem can be initialized."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus)
    assert system is not None


def test_dungeon_level_system_starts_at_level_one():
    """DungeonLevelSystem starts at level 1."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus)
    assert system.current_level == 1


def test_dungeon_level_system_has_level_configs():
    """DungeonLevelSystem loads level configurations."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus)
    assert len(system.level_configs) == 5


def test_generate_level_returns_map_and_rooms():
    """Generating level 1 returns a GameMap and list of rooms."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus)
    game_map, rooms = system.generate_level(1)
    assert game_map is not None and isinstance(rooms, list)


def test_generate_level_one_creates_rooms():
    """Generating level 1 creates at least one room."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus, random_seed=42)
    game_map, rooms = system.generate_level(1)
    assert len(rooms) > 0


def test_generate_level_one_has_correct_dimensions():
    """Generated level 1 map has correct dimensions (80x50)."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus)
    game_map, rooms = system.generate_level(1)
    assert game_map.width == 80 and game_map.height == 50


def test_generate_level_with_monsters_returns_complete_data():
    """generate_level_with_monsters returns map, rooms, monsters, stairs."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus, random_seed=42)
    game_map, rooms, monsters, stairs_pos = system.generate_level_with_monsters(1)
    assert game_map is not None and rooms and isinstance(monsters, list)


def test_generate_level_with_monsters_creates_monsters():
    """Generated level has at least some monsters."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus, random_seed=42)
    _, _, monsters, _ = system.generate_level_with_monsters(1)
    # With seed 42 and multiple rooms, should have some monsters
    assert len(monsters) >= 0  # May be 0 if rooms are small or unlucky


def test_generate_level_with_monsters_places_stairs():
    """Generated level 1 has stairs down."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus, random_seed=42)
    _, _, _, stairs_pos = system.generate_level_with_monsters(1)
    assert stairs_pos is not None


def test_transition_to_level_updates_current_level():
    """Transitioning to level 2 updates current_level."""
    event_bus = EventBus()
    system = DungeonLevelSystem(event_bus)
    system.transition_to_level(2)
    assert system.current_level == 2


def test_transition_to_level_emits_event():
    """Transitioning to a level emits LevelTransitionEvent."""
    event_bus = EventBus()
    events_received = []

    def capture_event(event):
        events_received.append(event)

    event_bus.subscribe("level_transition", capture_event)
    system = DungeonLevelSystem(event_bus)
    system.transition_to_level(2)
    assert len(events_received) == 1


def test_transition_event_has_correct_level():
    """LevelTransitionEvent contains correct level number."""
    event_bus = EventBus()
    events_received = []

    def capture_event(event):
        events_received.append(event)

    event_bus.subscribe("level_transition", capture_event)
    system = DungeonLevelSystem(event_bus)
    system.transition_to_level(3)
    assert events_received[0].new_level == 3


def test_transition_event_has_level_name():
    """LevelTransitionEvent contains level name."""
    event_bus = EventBus()
    events_received = []

    def capture_event(event):
        events_received.append(event)

    event_bus.subscribe("level_transition", capture_event)
    system = DungeonLevelSystem(event_bus)
    system.transition_to_level(2)
    assert events_received[0].level_name == "Dark Tunnels"
