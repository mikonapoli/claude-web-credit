"""Dungeon level system for procedural generation with difficulty scaling."""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
import os
import random

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.level import LevelComponent
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap
from roguelike.world.procgen import generate_dungeon, place_stairs
from roguelike.world.room import Room
from roguelike.engine.events import EventBus, LevelTransitionEvent


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
    max_items_per_room: int
    max_materials_per_room: int
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
            max_items_per_room=level_data.get("max_items_per_room", 1),
            max_materials_per_room=level_data.get("max_materials_per_room", 2),
            monster_spawn_rules=spawn_rules,
        )

    return levels


def create_scaled_monster(
    monster_type: str, position: Position, spawn_rule: MonsterSpawnRule
) -> ComponentEntity:
    """Create a monster with scaled stats based on spawn rule.

    Args:
        monster_type: Type of monster ("orc" or "troll")
        position: Monster position
        spawn_rule: Spawn rule with scaling factors

    Returns:
        Monster entity with scaled stats
    """
    # Base stats for monster types
    base_stats = {
        "orc": {"char": "o", "name": "Orc", "max_hp": 10, "power": 3, "defense": 0, "xp_value": 35},
        "troll": {"char": "T", "name": "Troll", "max_hp": 16, "power": 4, "defense": 1, "xp_value": 100},
    }

    if monster_type not in base_stats:
        raise ValueError(f"Unknown monster type: {monster_type}")

    stats = base_stats[monster_type]

    # Apply scaling
    scaled_hp = int(stats["max_hp"] * spawn_rule.hp_scale)
    scaled_power = int(stats["power"] * spawn_rule.power_scale)
    scaled_defense = int(stats["defense"] * spawn_rule.defense_scale)

    # Create monster entity with components
    monster = ComponentEntity(
        position=position,
        char=stats["char"],
        name=stats["name"],
        blocks_movement=True,
    )

    # Add components with scaled stats
    monster.add_component(HealthComponent(max_hp=scaled_hp))
    monster.add_component(CombatComponent(power=scaled_power, defense=scaled_defense))
    monster.add_component(LevelComponent(level=1, xp=0, xp_value=stats["xp_value"]))

    return monster


def place_monsters_scaled(
    room: Room, level_config: DungeonLevel
) -> List[ComponentEntity]:
    """Place monsters in a room with difficulty scaling.

    Args:
        room: Room to place monsters in
        level_config: Level configuration with spawn rules

    Returns:
        List of spawned monsters
    """
    num_monsters = random.randint(0, level_config.max_monsters_per_room)
    monsters: List[ComponentEntity] = []

    # Get all inner tile positions
    inner_positions = list(room.inner_tiles())

    for _ in range(num_monsters):
        if not inner_positions:
            break

        # Pick random position and remove it from available positions
        pos = random.choice(inner_positions)
        inner_positions.remove(pos)

        # Select monster type based on spawn chances
        roll = random.random()
        cumulative_chance = 0.0

        for monster_type, spawn_rule in level_config.monster_spawn_rules.items():
            cumulative_chance += spawn_rule.chance
            if roll < cumulative_chance:
                monsters.append(
                    create_scaled_monster(monster_type, pos, spawn_rule)
                )
                break

    return monsters


class DungeonLevelSystem:
    """Manages dungeon level generation with difficulty progression."""

    def __init__(
        self, event_bus: EventBus, random_seed: int | None = None
    ):
        """Initialize dungeon level system.

        Args:
            event_bus: Event bus for level transition events
            random_seed: Optional seed for reproducible generation
        """
        self.event_bus = event_bus
        self.current_level = 1
        self.level_configs = load_level_config()
        self.random_seed = random_seed

    def generate_level(
        self, level_number: int
    ) -> Tuple[GameMap, List[Room]]:
        """Generate a dungeon level with appropriate difficulty.

        Args:
            level_number: Level number to generate (1-5)

        Returns:
            Tuple of (game map, list of rooms)
        """
        if level_number not in self.level_configs:
            raise ValueError(
                f"Invalid level number: {level_number}. "
                f"Must be between 1 and {len(self.level_configs)}"
            )

        config = self.level_configs[level_number]

        # Generate dungeon layout
        game_map, rooms = generate_dungeon(
            width=config.width,
            height=config.height,
            max_rooms=config.max_rooms,
            min_room_size=config.min_room_size,
            max_room_size=config.max_room_size,
            random_seed=self.random_seed,
        )

        return game_map, rooms

    def generate_level_with_monsters(
        self, level_number: int
    ) -> Tuple[GameMap, List[Room], List[ComponentEntity], Position]:
        """Generate a complete level with monsters, items, materials, and stairs.

        Args:
            level_number: Level number to generate (1-5)

        Returns:
            Tuple of (game map, list of rooms, list of entities, stairs position)
            entities includes monsters, items, and crafting materials
        """
        from roguelike.world.procgen import place_items, place_crafting_materials

        config = self.level_configs[level_number]
        game_map, rooms = self.generate_level(level_number)

        # Place monsters, items, and materials in all rooms except the first (player spawn)
        entities: List[ComponentEntity] = []
        for room in rooms[1:]:
            # Place monsters
            room_monsters = place_monsters_scaled(room, config)
            entities.extend(room_monsters)

            # Place regular items
            room_items = place_items(room, config.max_items_per_room)
            entities.extend(room_items)

            # Place crafting materials
            room_materials = place_crafting_materials(room, config.max_materials_per_room)
            entities.extend(room_materials)

        # Place stairs down in the last room (unless it's the final level)
        stairs_pos = None
        if level_number < len(self.level_configs):
            stairs_pos = place_stairs(game_map, rooms[-1], "down")

        return game_map, rooms, entities, stairs_pos

    def transition_to_level(self, level_number: int) -> None:
        """Transition to a new level and emit event.

        Args:
            level_number: Level number to transition to
        """
        if level_number not in self.level_configs:
            raise ValueError(
                f"Cannot transition to level {level_number}. "
                f"Valid levels: 1-{len(self.level_configs)}"
            )

        self.current_level = level_number
        config = self.level_configs[level_number]

        # Emit level transition event
        self.event_bus.emit(
            LevelTransitionEvent(
                new_level=level_number, level_name=config.name
            )
        )
