"""Dungeon level system for procedural generation with difficulty scaling."""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
import os

from roguelike.entities.monster import Monster
from roguelike.world.game_map import GameMap
from roguelike.world.procgen import generate_dungeon
from roguelike.utils.position import Position
from roguelike.engine.events import EventBus


@dataclass
class MonsterSpawnRule:
    """Rules for spawning a specific monster type on a level."""

    chance: float
    hp_scale: float
    power_scale: float
    defense_scale: float


@dataclass
class DungeonLevel:
    """Configuration for a single dungeon level."""

    level_number: int
    name: str
    description: str
    width: int
    height: int
    max_rooms: int
    min_room_size: int
    max_room_size: int
    max_monsters_per_room: int
    monster_spawn_rules: Dict[str, MonsterSpawnRule]


def load_level_config(file_path: str = None) -> Dict[int, DungeonLevel]:
    """Load level configuration from JSON file.

    Args:
        file_path: Path to levels.json file. If None, uses default location.

    Returns:
        Dictionary mapping level number to DungeonLevel configuration
    """
    if file_path is None:
        # Default to data/levels.json in the roguelike package
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(
            current_dir, "..", "data", "levels.json"
        )

    with open(file_path, "r") as f:
        data = json.load(f)

    levels = {}
    for level_num_str, level_data in data.items():
        level_num = int(level_num_str)

        # Parse monster spawn rules
        spawn_rules = {}
        for monster_type, rule_data in level_data["monster_spawn_rules"].items():
            spawn_rules[monster_type] = MonsterSpawnRule(
                chance=rule_data["chance"],
                hp_scale=rule_data["hp_scale"],
                power_scale=rule_data["power_scale"],
                defense_scale=rule_data["defense_scale"],
            )

        levels[level_num] = DungeonLevel(
            level_number=level_num,
            name=level_data["name"],
            description=level_data["description"],
            width=level_data["width"],
            height=level_data["height"],
            max_rooms=level_data["max_rooms"],
            min_room_size=level_data["min_room_size"],
            max_room_size=level_data["max_room_size"],
            max_monsters_per_room=level_data["max_monsters_per_room"],
            monster_spawn_rules=spawn_rules,
        )

    return levels
