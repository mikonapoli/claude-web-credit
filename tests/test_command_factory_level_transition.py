"""Test that CommandFactory references are updated during level transitions."""

import pytest

from roguelike.commands.factory import CommandFactory
from roguelike.components.entity import ComponentEntity
from roguelike.engine.events import EventBus
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


def test_command_factory_update_context_updates_game_map():
    """CommandFactory.update_context() updates game_map reference."""
    event_bus = EventBus()
    old_map = GameMap(width=80, height=50)
    new_map = GameMap(width=80, height=50)

    player = ComponentEntity(Position(5, 5), "@", "Player")
    entities = []
    fov_map = FOVMap(old_map)
    message_log = MessageLog()

    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(old_map)
    ai_system = AISystem(combat_system, movement_system, old_map, None)
    status_effects_system = StatusEffectsSystem(event_bus)
    targeting_system = TargetingSystem()

    factory = CommandFactory(
        player=player,
        entities=entities,
        game_map=old_map,
        fov_map=fov_map,
        fov_radius=8,
        combat_system=combat_system,
        movement_system=movement_system,
        ai_system=ai_system,
        status_effects_system=status_effects_system,
        targeting_system=targeting_system,
        message_log=message_log,
        event_bus=event_bus,
    )

    # Verify initial reference
    assert factory.game_map is old_map

    # Update context with new map
    factory.update_context(game_map=new_map)

    # Verify reference was updated
    assert factory.game_map is new_map
    assert factory.game_map is not old_map


def test_command_factory_update_context_updates_fov_map():
    """CommandFactory.update_context() updates fov_map reference."""
    event_bus = EventBus()
    game_map = GameMap(width=80, height=50)
    old_fov_map = FOVMap(game_map)
    new_fov_map = FOVMap(game_map)

    player = ComponentEntity(Position(5, 5), "@", "Player")
    entities = []
    message_log = MessageLog()

    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map, None)
    status_effects_system = StatusEffectsSystem(event_bus)
    targeting_system = TargetingSystem()

    factory = CommandFactory(
        player=player,
        entities=entities,
        game_map=game_map,
        fov_map=old_fov_map,
        fov_radius=8,
        combat_system=combat_system,
        movement_system=movement_system,
        ai_system=ai_system,
        status_effects_system=status_effects_system,
        targeting_system=targeting_system,
        message_log=message_log,
        event_bus=event_bus,
    )

    # Verify initial reference
    assert factory.fov_map is old_fov_map

    # Update context with new FOV map
    factory.update_context(fov_map=new_fov_map)

    # Verify reference was updated
    assert factory.fov_map is new_fov_map
    assert factory.fov_map is not old_fov_map


def test_command_factory_update_context_updates_multiple_references():
    """CommandFactory.update_context() can update multiple references at once."""
    event_bus = EventBus()
    old_map = GameMap(width=80, height=50)
    new_map = GameMap(width=80, height=50)
    old_fov_map = FOVMap(old_map)
    new_fov_map = FOVMap(new_map)

    player = ComponentEntity(Position(5, 5), "@", "Player")
    old_entities = []
    new_entities = [ComponentEntity(Position(10, 10), "o", "Orc")]
    message_log = MessageLog()

    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(old_map)
    ai_system = AISystem(combat_system, movement_system, old_map, None)
    status_effects_system = StatusEffectsSystem(event_bus)
    targeting_system = TargetingSystem()

    factory = CommandFactory(
        player=player,
        entities=old_entities,
        game_map=old_map,
        fov_map=old_fov_map,
        fov_radius=8,
        combat_system=combat_system,
        movement_system=movement_system,
        ai_system=ai_system,
        status_effects_system=status_effects_system,
        targeting_system=targeting_system,
        message_log=message_log,
        event_bus=event_bus,
        stairs_pos=Position(5, 5),
    )

    # Verify initial references
    assert factory.game_map is old_map
    assert factory.fov_map is old_fov_map
    assert factory.entities is old_entities
    assert factory.stairs_pos == Position(5, 5)

    # Update all level-transition-related references at once
    factory.update_context(
        entities=new_entities,
        game_map=new_map,
        fov_map=new_fov_map,
        stairs_pos=Position(15, 15),
    )

    # Verify all references were updated
    assert factory.game_map is new_map
    assert factory.fov_map is new_fov_map
    assert factory.entities is new_entities
    assert factory.stairs_pos == Position(15, 15)
