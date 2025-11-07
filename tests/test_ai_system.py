"""Tests for AISystem."""

from roguelike.engine.events import EventBus
from roguelike.entities.monster import create_orc, create_troll
# from roguelike.entities.player import Player
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles


def test_ai_system_creation():
    """AISystem can be created with required dependencies."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)

    ai_system = AISystem(combat_system, movement_system, game_map)

    assert ai_system.combat_system == combat_system
    assert ai_system.movement_system == movement_system
    assert ai_system.game_map == game_map
    assert len(ai_system.monster_ais) == 0


def test_register_monster():
    """Can register a monster with AI system."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    orc = create_orc(Position(5, 5))
    ai_system.register_monster(orc)

    assert orc in ai_system.monster_ais


def test_register_monster_idempotent():
    """Registering same monster twice does not create duplicate."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    orc = create_orc(Position(5, 5))
    ai_system.register_monster(orc)
    ai_system.register_monster(orc)

    assert len(ai_system.monster_ais) == 1


def test_unregister_monster():
    """Can unregister a monster from AI system."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    orc = create_orc(Position(5, 5))
    ai_system.register_monster(orc)
    ai_system.unregister_monster(orc)

    assert orc not in ai_system.monster_ais


def test_unregister_nonexistent_monster():
    """Unregistering nonexistent monster does not error."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    orc = create_orc(Position(5, 5))
    ai_system.unregister_monster(orc)  # Should not raise


def test_process_turns_no_monsters():
    """Processing turns with no monsters works."""
    game_map = GameMap(20, 20)
    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    player_died = ai_system.process_turns(player, [player])

    assert not player_died


def test_process_turns_skips_dead_monster():
    """Processing turns skips dead monsters."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(5, 5))
    orc.take_damage(100)  # Kill the orc

    ai_system.register_monster(orc)
    player_died = ai_system.process_turns(player, [player, orc])

    assert not player_died
    assert not orc.is_alive


def test_process_turns_monster_moves():
    """Monster moves toward player when within chase range."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    # Place orc 5 tiles away (within chase range of 10)
    orc = create_orc(Position(7, 7))
    original_pos = orc.position

    ai_system.register_monster(orc)
    player_died = ai_system.process_turns(player, [player, orc])

    assert not player_died
    assert orc.position != original_pos  # Orc should have moved


def test_process_turns_monster_attacks():
    """Monster attacks player when adjacent."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    original_hp = player.hp

    # Place orc adjacent to player
    orc = create_orc(Position(10, 11))

    ai_system.register_monster(orc)
    player_died = ai_system.process_turns(player, [player, orc])

    # Player should have taken damage
    assert player.hp < original_hp


def test_process_turns_player_death():
    """Returns True when player dies."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    player.hp = 1  # Set to low HP

    # Place strong troll adjacent
    troll = create_troll(Position(10, 11))

    ai_system.register_monster(troll)
    player_died = ai_system.process_turns(player, [player, troll])

    assert player_died
    assert not player.is_alive


def test_process_turns_emits_combat_events():
    """Combat events are emitted when monster attacks."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    events_received = []

    def on_combat(event):
        events_received.append(event)

    event_bus.subscribe("combat", on_combat)

    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(10, 11))

    ai_system.register_monster(orc)
    ai_system.process_turns(player, [player, orc])

    # Should have received combat event
    assert len(events_received) == 1
    assert events_received[0].attacker_name == "Orc"


def test_process_turns_skips_unregistered_monster():
    """Unregistered monsters are skipped."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    event_bus = EventBus()
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)

    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(10, 11))
    original_hp = player.hp

    # Don't register orc - it should not act
    player_died = ai_system.process_turns(player, [player, orc])

    assert not player_died
    assert player.hp == original_hp  # No damage taken
