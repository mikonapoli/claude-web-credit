"""Procedural generation for dungeons."""

import random
from typing import List, Optional

from roguelike.data.entity_loader import EntityLoader
from roguelike.entities.item import (
    Item,
    create_banana_peel,
    create_cheese_wheel,
    create_coffee,
    create_cursed_ring,
    create_defense_potion,
    create_gigantism_potion,
    create_greater_healing_potion,
    create_healing_potion,
    create_invisibility_potion,
    create_lucky_coin,
    create_rubber_chicken,
    create_scroll_confusion,
    create_scroll_fireball,
    create_scroll_lightning,
    create_scroll_magic_mapping,
    create_scroll_teleport,
    create_shrinking_potion,
    create_speed_potion,
    create_strength_potion,
)
from roguelike.components.entity import ComponentEntity
from roguelike.components.factories import (
    create_orc,
    create_troll,
    # Weapons
    create_wooden_club,
    create_iron_sword,
    create_steel_sword,
    create_enchanted_blade,
    create_battle_axe,
    # Armor
    create_leather_armor,
    create_chainmail,
    create_plate_armor,
    create_dragon_scale_armor,
    # Helmets
    create_leather_helmet,
    create_steel_helmet,
    create_crown_of_kings,
    # Boots
    create_leather_boots,
    create_steel_boots,
    create_boots_of_speed,
    # Gloves
    create_leather_gloves,
    create_gauntlets,
    # Rings
    create_ring_of_power,
    create_ring_of_protection,
    create_ring_of_vitality,
    # Amulets
    create_amulet_of_strength,
    create_amulet_of_defense,
    create_amulet_of_life,
)
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap
from roguelike.world.room import Room
from roguelike.world.tile import Tiles


def create_horizontal_tunnel(game_map: GameMap, x1: int, x2: int, y: int) -> None:
    """Carve a horizontal tunnel.

    Args:
        game_map: Map to modify
        x1: Start x coordinate
        x2: End x coordinate
        y: Y coordinate
    """
    for x in range(min(x1, x2), max(x1, x2) + 1):
        pos = Position(x, y)
        if game_map.in_bounds(pos):
            game_map.set_tile(pos, Tiles.FLOOR)


def create_vertical_tunnel(game_map: GameMap, y1: int, y2: int, x: int) -> None:
    """Carve a vertical tunnel.

    Args:
        game_map: Map to modify
        y1: Start y coordinate
        y2: End y coordinate
        x: X coordinate
    """
    for y in range(min(y1, y2), max(y1, y2) + 1):
        pos = Position(x, y)
        if game_map.in_bounds(pos):
            game_map.set_tile(pos, Tiles.FLOOR)


def carve_room(game_map: GameMap, room: Room) -> None:
    """Carve out a room in the map.

    Args:
        game_map: Map to modify
        room: Room to carve
    """
    for pos in room.inner_tiles():
        if game_map.in_bounds(pos):
            game_map.set_tile(pos, Tiles.FLOOR)


def place_monsters(room: Room, max_monsters: int) -> List[ComponentEntity]:
    """Place monsters randomly in a room.

    Args:
        room: Room to place monsters in
        max_monsters: Maximum number of monsters

    Returns:
        List of spawned monsters
    """
    num_monsters = random.randint(0, max_monsters)
    monsters: List[ComponentEntity] = []

    # Get all inner tile positions
    inner_positions = list(room.inner_tiles())

    for _ in range(num_monsters):
        if not inner_positions:
            break

        # Pick random position and remove it from available positions
        pos = random.choice(inner_positions)
        inner_positions.remove(pos)

        # 80% chance of orc, 20% chance of troll
        if random.random() < 0.8:
            monsters.append(create_orc(pos))
        else:
            monsters.append(create_troll(pos))

    return monsters


def place_stairs(
    game_map: GameMap, room: Room, stairs_type: str = "down"
) -> Position:
    """Place stairs in the center of a room.

    Args:
        game_map: Map to modify
        room: Room to place stairs in
        stairs_type: Type of stairs ("down" or "up")

    Returns:
        Position where stairs were placed
    """
    stairs_pos = room.center

    if stairs_type == "down":
        game_map.set_tile(stairs_pos, Tiles.STAIRS_DOWN)
    else:
        game_map.set_tile(stairs_pos, Tiles.STAIRS_UP)

    return stairs_pos
def place_items(room: Room, max_items: int) -> List[Item]:
    """Place items randomly in a room.

    Args:
        room: Room to place items in
        max_items: Maximum number of items

    Returns:
        List of spawned items
    """
    num_items = random.randint(0, max_items)
    items: List[Item] = []

    # Get all inner tile positions
    inner_positions = list(room.inner_tiles())

    # Item spawn chances with weights
    item_spawners = [
        (create_healing_potion, 30),  # Common
        (create_greater_healing_potion, 15),  # Uncommon
        (create_strength_potion, 10),  # Uncommon
        (create_defense_potion, 10),  # Uncommon
        (create_speed_potion, 5),  # Rare
        (create_scroll_fireball, 5),  # Rare
        (create_scroll_lightning, 5),  # Rare
        (create_scroll_confusion, 5),  # Rare
        (create_scroll_teleport, 3),  # Very rare
        (create_scroll_magic_mapping, 3),  # Very rare
        (create_invisibility_potion, 2),  # Very rare
        (create_coffee, 8),  # Common quirky
        (create_cheese_wheel, 3),  # Rare
        (create_lucky_coin, 2),  # Very rare
        (create_banana_peel, 5),  # Uncommon quirky
        (create_rubber_chicken, 4),  # Uncommon quirky
        (create_gigantism_potion, 2),  # Very rare
        (create_shrinking_potion, 2),  # Very rare
        (create_cursed_ring, 1),  # Ultra rare
    ]

    # Calculate total weight for proper weighted selection
    total_weight = sum(weight for _, weight in item_spawners)

    for _ in range(num_items):
        if not inner_positions:
            break

        # Pick random position and remove it from available positions
        pos = random.choice(inner_positions)
        inner_positions.remove(pos)

        # Choose item based on weighted random selection
        roll = random.randint(1, total_weight)
        cumulative = 0
        for spawner, weight in item_spawners:
            cumulative += weight
            if roll <= cumulative:
                items.append(spawner(pos))
                break

    return items


def place_crafting_materials(room: Room, max_materials: int) -> List["ComponentEntity"]:
    """Place crafting materials randomly in a room.

    Args:
        room: Room to place materials in
        max_materials: Maximum number of materials

    Returns:
        List of spawned crafting material entities
    """
    num_materials = random.randint(0, max_materials)
    materials: List["ComponentEntity"] = []

    # Get all inner tile positions
    inner_positions = list(room.inner_tiles())

    # Crafting material types with spawn weights
    material_types = [
        ("moonleaf", 15),           # Common herbal
        ("mana_crystal", 12),       # Common magical
        ("nightshade", 10),         # Common sinister
        ("purifying_salt", 10),     # Common purifying
        ("iron_ore", 8),            # Common metallic
        ("volcanic_ash", 8),        # Uncommon volcanic
        ("sulfur", 8),              # Uncommon sulfuric
        ("frost_essence", 7),       # Uncommon boreal
        ("coffee", 6),              # Uncommon energizing
        ("blessed_water", 5),       # Rare holy
        ("ancient_parchment", 5),   # Rare parchment
        ("shadow_ink", 4),          # Rare sinister
        ("dragon_scale", 3),        # Very rare magical
        ("runic_essence", 3),       # Very rare runic
        ("phoenix_feather", 2),     # Ultra rare fiery
        ("thunder_stone", 2),       # Ultra rare electric
        ("giants_tears", 2),        # Ultra rare empowering
        ("pixie_dust", 2),          # Ultra rare ethereal
    ]

    # Calculate total weight for proper weighted selection
    total_weight = sum(weight for _, weight in material_types)

    # Create entity loader for crafting materials
    entity_loader = EntityLoader()

    for _ in range(num_materials):
        if not inner_positions:
            break

        # Pick random position and remove it from available positions
        pos = random.choice(inner_positions)
        inner_positions.remove(pos)

        # Choose material based on weighted random selection
        roll = random.randint(1, total_weight)
        cumulative = 0
        for material_type, weight in material_types:
            cumulative += weight
            if roll <= cumulative:
                materials.append(entity_loader.create_entity(material_type, pos))
                break

    return materials


def place_equipment(room: Room, max_equipment: int, dungeon_level: int = 1) -> List[ComponentEntity]:
    """Place equipment items randomly in a room.

    Args:
        room: Room to place equipment in
        max_equipment: Maximum number of equipment items
        dungeon_level: Current dungeon level (affects rarity)

    Returns:
        List of spawned equipment items
    """
    num_equipment = random.randint(0, max_equipment)
    equipment_items: List[ComponentEntity] = []

    # Get all inner tile positions
    inner_positions = list(room.inner_tiles())

    # Equipment spawn chances with weights, adjusted by level
    # Early game: Common equipment (leather, wooden, iron)
    # Mid game: Uncommon equipment (steel, chainmail)
    # Late game: Rare equipment (enchanted, plate, dragon scale, crowns, rings, amulets)

    # Define equipment spawners by tier
    common_equipment = [
        (create_wooden_club, 15),
        (create_iron_sword, 12),
        (create_leather_armor, 12),
        (create_leather_helmet, 10),
        (create_leather_boots, 10),
        (create_leather_gloves, 10),
    ]

    uncommon_equipment = [
        (create_steel_sword, 8),
        (create_chainmail, 8),
        (create_steel_helmet, 6),
        (create_steel_boots, 6),
        (create_gauntlets, 5),
        (create_ring_of_power, 3),
        (create_ring_of_protection, 3),
    ]

    rare_equipment = [
        (create_enchanted_blade, 4),
        (create_battle_axe, 3),
        (create_plate_armor, 4),
        (create_crown_of_kings, 2),
        (create_boots_of_speed, 3),
        (create_ring_of_vitality, 3),
        (create_amulet_of_strength, 2),
        (create_amulet_of_defense, 2),
        (create_amulet_of_life, 2),
    ]

    legendary_equipment = [
        (create_dragon_scale_armor, 1),
    ]

    # Build equipment pool based on dungeon level
    equipment_spawners = []

    if dungeon_level >= 1:
        equipment_spawners.extend(common_equipment)
    if dungeon_level >= 2:
        equipment_spawners.extend(uncommon_equipment)
    if dungeon_level >= 3:
        equipment_spawners.extend(rare_equipment)
    if dungeon_level >= 4:
        equipment_spawners.extend(legendary_equipment)

    # Calculate total weight
    total_weight = sum(weight for _, weight in equipment_spawners)

    if total_weight == 0:
        return equipment_items

    for _ in range(num_equipment):
        if not inner_positions:
            break

        # Pick random position and remove it from available positions
        pos = random.choice(inner_positions)
        inner_positions.remove(pos)

        # Choose equipment based on weighted random selection
        roll = random.randint(1, total_weight)
        cumulative = 0
        for spawner, weight in equipment_spawners:
            cumulative += weight
            if roll <= cumulative:
                equipment_items.append(spawner(pos))
                break

    return equipment_items


def generate_dungeon(
    width: int,
    height: int,
    max_rooms: int,
    min_room_size: int,
    max_room_size: int,
    random_seed: int | None = None,
) -> tuple[GameMap, List[Room]]:
    """Generate a dungeon using room-and-corridors algorithm.

    Args:
        width: Map width
        height: Map height
        max_rooms: Maximum number of rooms to attempt
        min_room_size: Minimum room dimension
        max_room_size: Maximum room dimension
        random_seed: Optional seed for reproducible generation

    Returns:
        Tuple of (generated map, list of rooms)
    """
    if random_seed is not None:
        random.seed(random_seed)

    game_map = GameMap(width, height)
    rooms: List[Room] = []

    for _ in range(max_rooms):
        # Generate random room dimensions
        room_width = random.randint(min_room_size, max_room_size)
        room_height = random.randint(min_room_size, max_room_size)

        # Generate random position
        x = random.randint(0, width - room_width - 1)
        y = random.randint(0, height - room_height - 1)

        new_room = Room(x, y, room_width, room_height)

        # Check if room intersects with existing rooms
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue

        # Room is valid, carve it out
        carve_room(game_map, new_room)

        # Connect to previous room with tunnels
        if rooms:
            # Connect centers of rooms
            prev_center = rooms[-1].center
            new_center = new_room.center

            # 50% chance to go horizontal first, 50% vertical first
            if random.random() < 0.5:
                create_horizontal_tunnel(game_map, prev_center.x, new_center.x, prev_center.y)
                create_vertical_tunnel(game_map, prev_center.y, new_center.y, new_center.x)
            else:
                create_vertical_tunnel(game_map, prev_center.y, new_center.y, prev_center.x)
                create_horizontal_tunnel(game_map, prev_center.x, new_center.x, new_center.y)

        rooms.append(new_room)

    return game_map, rooms
