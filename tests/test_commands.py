"""Tests for command pattern."""

from tests.test_helpers import create_test_entity, create_test_player, create_test_monster
from roguelike.commands.game_commands import MoveCommand, QuitCommand, WaitCommand
from roguelike.commands.executor import CommandExecutor
from roguelike.engine.events import EventBus
# from roguelike.entities.player import Player
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.turn_manager import TurnManager
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles


def test_quit_command_execution():
    """QuitCommand returns should_quit=True."""
    cmd = QuitCommand()
    result = cmd.execute()

    assert result.success
    assert not result.turn_consumed
    assert result.should_quit


def test_quit_command_not_undoable():
    """QuitCommand cannot be undone."""
    cmd = QuitCommand()
    assert not cmd.can_undo()


def test_wait_command_execution():
    """WaitCommand consumes a turn."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))

    cmd = WaitCommand(
        player=player,
        entities=[player],
        ai_system=ai_system,
        combat_system=combat_system,
        status_effects_system=None,
    )
    result = cmd.execute()

    assert result.success
    assert result.turn_consumed
    assert not result.should_quit


def test_move_command_execution():
    """MoveCommand moves the player."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    fov_map = FOVMap(game_map)

    cmd = MoveCommand(
        player=player,
        dx=0,
        dy=1,
        entities=[player],
        game_map=game_map,
        fov_map=fov_map,
        fov_radius=8,
        movement_system=movement_system,
        combat_system=combat_system,
        ai_system=ai_system,
        status_effects_system=None,
    )
    result = cmd.execute()

    assert result.success
    assert result.turn_consumed
    assert player.position == Position(10, 11)


def test_move_command_undo():
    """MoveCommand can be undone."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    fov_map = FOVMap(game_map)

    cmd = MoveCommand(
        player=player,
        dx=0,
        dy=1,
        entities=[player],
        game_map=game_map,
        fov_map=fov_map,
        fov_radius=8,
        movement_system=movement_system,
        combat_system=combat_system,
        ai_system=ai_system,
        status_effects_system=None,
    )
    cmd.execute()

    assert cmd.can_undo()
    cmd.undo()
    assert player.position == Position(10, 10)


def test_move_command_invalid_direction():
    """MoveCommand with invalid direction returns false when blocked."""
    game_map = GameMap(20, 20)
    # Set all tiles to walls (blocking)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    fov_map = FOVMap(game_map)

    # Try to move into a wall
    cmd = MoveCommand(
        player=player,
        dx=1,
        dy=0,
        entities=[player],
        game_map=game_map,
        fov_map=fov_map,
        fov_radius=8,
        movement_system=movement_system,
        combat_system=combat_system,
        ai_system=ai_system,
        status_effects_system=None,
    )
    result = cmd.execute()

    assert not result.success
    assert not result.turn_consumed


def test_command_executor_execute():
    """CommandExecutor can execute commands."""
    executor = CommandExecutor()
    cmd = QuitCommand()

    result = executor.execute(cmd)

    assert result.success
    assert result.should_quit


def test_command_executor_history():
    """CommandExecutor stores undoable commands in history."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    player = create_test_player(Position(10, 10))
    fov_map = FOVMap(game_map)

    executor = CommandExecutor()
    cmd = MoveCommand(
        player=player,
        dx=0,
        dy=1,
        entities=[player],
        game_map=game_map,
        fov_map=fov_map,
        fov_radius=8,
        movement_system=movement_system,
        combat_system=combat_system,
        ai_system=ai_system,
        status_effects_system=None,
    )
    executor.execute(cmd)

    assert executor.get_history_size() == 1


def test_command_executor_undo():
    """CommandExecutor can undo commands."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    player = create_test_player(Position(10, 10))
    fov_map = FOVMap(game_map)

    executor = CommandExecutor()
    cmd = MoveCommand(
        player=player,
        dx=0,
        dy=1,
        entities=[player],
        game_map=game_map,
        fov_map=fov_map,
        fov_radius=8,
        movement_system=movement_system,
        combat_system=combat_system,
        ai_system=ai_system,
        status_effects_system=None,
    )
    executor.execute(cmd)

    assert executor.can_undo()
    executor.undo()
    assert player.position == Position(10, 10)


def test_command_executor_redo():
    """CommandExecutor can redo commands."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    player = create_test_player(Position(10, 10))
    fov_map = FOVMap(game_map)

    executor = CommandExecutor()
    cmd = MoveCommand(
        player=player,
        dx=0,
        dy=1,
        entities=[player],
        game_map=game_map,
        fov_map=fov_map,
        fov_radius=8,
        movement_system=movement_system,
        combat_system=combat_system,
        ai_system=ai_system,
        status_effects_system=None,
    )
    executor.execute(cmd)
    executor.undo()

    assert executor.can_redo()
    executor.redo()
    assert player.position == Position(10, 11)


def test_command_executor_clear_history():
    """CommandExecutor can clear history."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    player = create_test_player(Position(10, 10))
    fov_map = FOVMap(game_map)

    executor = CommandExecutor()
    cmd = MoveCommand(
        player=player,
        dx=0,
        dy=1,
        entities=[player],
        game_map=game_map,
        fov_map=fov_map,
        fov_radius=8,
        movement_system=movement_system,
        combat_system=combat_system,
        ai_system=ai_system,
        status_effects_system=None,
    )
    executor.execute(cmd)

    executor.clear_history()
    assert executor.get_history_size() == 0
    assert not executor.can_undo()


def test_command_executor_max_history():
    """CommandExecutor respects max_history limit."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    player = create_test_player(Position(10, 10))
    fov_map = FOVMap(game_map)

    executor = CommandExecutor(max_history=2)

    # Execute 3 commands
    for i in range(3):
        cmd = MoveCommand(
            player=player,
            dx=1,
            dy=0,
            entities=[player],
            game_map=game_map,
            fov_map=fov_map,
            fov_radius=8,
            movement_system=movement_system,
            combat_system=combat_system,
            ai_system=ai_system,
            status_effects_system=None,
        )
        executor.execute(cmd)

    # Should only keep last 2
    assert executor.get_history_size() == 2


def test_command_executor_no_undo_when_empty():
    """CommandExecutor cannot undo with empty history."""
    executor = CommandExecutor()
    assert not executor.can_undo()
    assert not executor.undo()


def test_command_executor_no_redo_when_empty():
    """CommandExecutor cannot redo with empty history."""
    executor = CommandExecutor()
    assert not executor.can_redo()
    assert not executor.redo()


def test_use_item_command_rejects_targeted_items():
    """UseItemCommand rejects items that require targeting."""
    from roguelike.commands.inventory_commands import UseItemCommand
    from roguelike.entities.item import create_scroll_confusion
    from roguelike.systems.item_system import ItemSystem
    from roguelike.systems.status_effects import StatusEffectsSystem

    event_bus = EventBus()
    status_effects_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_effects_system)
    player = create_test_player(Position(10, 10))

    # Add a confusion scroll to inventory
    scroll = create_scroll_confusion(Position(0, 0))
    player.inventory.add(scroll)

    # Try to use it via UseItemCommand (should fail - requires targeting)
    cmd = UseItemCommand(player, scroll)
    result = cmd.execute()

    assert not result.success
    assert not result.turn_consumed
    # Item should still be in inventory (not consumed)
    assert player.inventory.get_item_by_index(0) == scroll


def test_use_item_command_allows_non_targeted_items():
    """UseItemCommand works for items that don't require targeting."""
    from roguelike.commands.inventory_commands import UseItemCommand
    from roguelike.entities.item import create_healing_potion
    from roguelike.systems.item_system import ItemSystem
    from roguelike.systems.status_effects import StatusEffectsSystem

    event_bus = EventBus()
    status_effects_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_effects_system)
    player = create_test_player(Position(10, 10))

    # Damage player so healing works
    player.take_damage(10)

    # Add a healing potion to inventory
    potion = create_healing_potion(Position(0, 0))
    player.inventory.add(potion)

    # Use it via UseItemCommand (should succeed - doesn't require targeting)
    cmd = UseItemCommand(player, potion)
    result = cmd.execute()

    assert result.success
    assert result.turn_consumed
    # Item should be consumed (removed from inventory)
    assert player.inventory.get_item_by_index(0) is None
