"""Tests for TurnManager."""

from roguelike.engine.events import EventBus
from roguelike.entities.monster import create_orc, create_troll
from roguelike.entities.player import Player
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.turn_manager import TurnManager
from roguelike.ui.input_handler import Action
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles


def test_turn_manager_creation():
    """TurnManager can be created with required systems."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    assert turn_manager.combat_system == combat_system
    assert turn_manager.movement_system == movement_system
    assert turn_manager.ai_system == ai_system


def test_handle_quit_action():
    """Quit action returns correct flags."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    fov_map = FOVMap(game_map)

    turn_consumed, should_quit = turn_manager.handle_player_action(
        Action.QUIT, player, [player], game_map, fov_map, 8
    )

    assert not turn_consumed
    assert should_quit


def test_handle_wait_action():
    """Wait action consumes turn."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    fov_map = FOVMap(game_map)

    turn_consumed, should_quit = turn_manager.handle_player_action(
        Action.WAIT, player, [player], game_map, fov_map, 8
    )

    assert turn_consumed
    assert not should_quit


def test_handle_movement_action():
    """Movement action moves player."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    fov_map = FOVMap(game_map)

    turn_consumed, should_quit = turn_manager.handle_player_action(
        Action.MOVE_UP, player, [player], game_map, fov_map, 8
    )

    assert turn_consumed
    assert not should_quit
    assert player.position == Position(10, 9)


def test_handle_movement_blocked_by_wall():
    """Movement into wall doesn't consume turn."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    # Leave (10, 9) as wall

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    fov_map = FOVMap(game_map)

    turn_consumed, should_quit = turn_manager.handle_player_action(
        Action.MOVE_UP, player, [player], game_map, fov_map, 8
    )

    assert not turn_consumed
    assert not should_quit
    assert player.position == Position(10, 10)


def test_handle_attack_monster():
    """Attacking monster consumes turn."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    orc = create_orc(Position(10, 11))
    fov_map = FOVMap(game_map)

    turn_consumed, should_quit = turn_manager.handle_player_action(
        Action.MOVE_DOWN, player, [player, orc], game_map, fov_map, 8
    )

    assert turn_consumed
    assert not should_quit
    assert player.position == Position(10, 10)  # Didn't move
    assert orc.hp < orc.max_hp  # Took damage


def test_process_turn_with_quit():
    """Process turn returns False on quit."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    fov_map = FOVMap(game_map)

    continue_game = turn_manager.process_turn(
        Action.QUIT, player, [player], game_map, fov_map, 8
    )

    assert not continue_game


def test_process_turn_with_movement():
    """Process turn handles movement and enemy turns."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    orc = create_orc(Position(7, 7))
    ai_system.register_monster(orc)
    fov_map = FOVMap(game_map)

    original_orc_pos = orc.position

    continue_game = turn_manager.process_turn(
        Action.MOVE_UP, player, [player, orc], game_map, fov_map, 8
    )

    assert continue_game
    assert player.position == Position(10, 9)
    # Orc should have moved toward player
    assert orc.position != original_orc_pos


def test_process_turn_player_death():
    """Process turn returns False when player dies."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    player.hp = 1  # Low HP

    troll = create_troll(Position(10, 11))
    ai_system.register_monster(troll)
    fov_map = FOVMap(game_map)

    continue_game = turn_manager.process_turn(
        Action.WAIT, player, [player, troll], game_map, fov_map, 8
    )

    assert not continue_game
    assert not player.is_alive


def test_process_turn_no_enemy_turns_on_invalid_action():
    """Enemy turns don't process if player action didn't consume turn."""
    game_map = GameMap(20, 20)
    # Player at (10, 10) on floor
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    # Wall at (10, 9)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    turn_manager = TurnManager(combat_system, movement_system, ai_system)

    player = Player(Position(10, 10))
    original_hp = player.hp

    # Place orc adjacent that would attack if turn processed
    for y in range(20):
        for x in range(20):
            if (x, y) != (10, 9):  # Keep wall at (10,9)
                game_map.set_tile(Position(x, y), Tiles.FLOOR)

    orc = create_orc(Position(10, 11))
    ai_system.register_monster(orc)
    fov_map = FOVMap(game_map)

    # Try to move into wall - shouldn't consume turn
    continue_game = turn_manager.process_turn(
        Action.MOVE_UP, player, [player, orc], game_map, fov_map, 8
    )

    assert continue_game
    assert player.position == Position(10, 10)
    # Player shouldn't have taken damage because turn wasn't consumed
    assert player.hp == original_hp
