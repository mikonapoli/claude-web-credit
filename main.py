"""Main entry point for the roguelike game."""

from roguelike.engine.game_engine import GameEngine
from roguelike.entities.player import Player
from roguelike.ui.renderer import Renderer
from roguelike.world.procgen import generate_dungeon, place_monsters


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

    # Place player in the center of the first room
    player_start = rooms[0].center
    player = Player(position=player_start)

    # Spawn monsters in all rooms except the first (player's room)
    entities = []
    for room in rooms[1:]:
        monsters = place_monsters(room, max_monsters_per_room)
        entities.extend(monsters)

    # Create renderer
    renderer = Renderer(screen_width, screen_height, "Roguelike Adventure")

    # Create and run the game engine
    engine = GameEngine(game_map=game_map, player=player, entities=entities)
    engine.run(renderer)


if __name__ == "__main__":
    main()
