"""Procedural generation for dungeons."""

import random
from typing import List, Optional

from roguelike.entities.monster import Monster, create_orc, create_troll
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


def place_monsters(room: Room, max_monsters: int) -> List[Monster]:
    """Place monsters randomly in a room.

    Args:
        room: Room to place monsters in
        max_monsters: Maximum number of monsters

    Returns:
        List of spawned monsters
    """
    num_monsters = random.randint(0, max_monsters)
    monsters: List[Monster] = []

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
