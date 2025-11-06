"""Main entry point for the roguelike game."""

from roguelike.engine.game_engine import GameEngine
from roguelike.engine.events import EventBus
from roguelike.entities.player import Player
from roguelike.systems.level_system import DungeonLevelSystem
from roguelike.ui.renderer import Renderer
from roguelike.world.procgen import generate_dungeon


def main():
    """Initialize and run the game."""
    # Game configuration
    screen_width = 80
    screen_height = 50
    message_log_height = 7
    map_height = screen_height - message_log_height
    max_monsters_per_room = 2

    # Generate the dungeon
    game_map, rooms = generate_dungeon(
        width=screen_width,
        height=map_height,
        max_rooms=30,
        min_room_size=6,
        max_room_size=10,
    )

    # Create event bus and dungeon level system
    event_bus = EventBus()
    level_system = DungeonLevelSystem(event_bus)

    # Generate the first dungeon level with scaled monsters
    game_map, rooms, monsters, stairs_pos = level_system.generate_level_with_monsters(1)

    # Place player in the center of the first room
    player_start = rooms[0].center
    player = Player(position=player_start)

    # Create renderer
    renderer = Renderer(screen_width, screen_height, "Roguelike Adventure")

    # Create and run the game engine
    engine = GameEngine(game_map=game_map, player=player, entities=monsters)
    engine.run(renderer)


if __name__ == "__main__":
    main()
