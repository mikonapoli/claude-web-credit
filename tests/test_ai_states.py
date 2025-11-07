"""Tests for AI State pattern implementation."""

from roguelike.components.factories import create_orc
from roguelike.systems.ai import (
    AIState,
    IdleState,
    ChaseState,
    AttackState,
    MonsterAI,
    _idle_state,
    _chase_state,
    _attack_state,
)
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles
from tests.test_helpers import create_test_player


def test_idle_state_returns_none():
    """IdleState always returns None (no movement)."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(15, 15))

    state = IdleState()
    result = state.update(orc, player, game_map, [player, orc])

    assert result is None


def test_attack_state_returns_none():
    """AttackState always returns None (attack handled by AISystem)."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(10, 11))

    state = AttackState()
    result = state.update(orc, player, game_map, [player, orc])

    assert result is None


def test_chase_state_moves_toward_player():
    """ChaseState returns position one step closer to player."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(7, 7))

    state = ChaseState()
    result = state.update(orc, player, game_map, [player, orc])

    assert result is not None
    # Should move closer to player
    assert result.x >= 7 and result.x <= 8
    assert result.y >= 7 and result.y <= 8


def test_monster_ai_starts_in_idle_state():
    """MonsterAI starts in IdleState by default."""
    orc = create_orc(Position(10, 10))
    ai = MonsterAI(orc)

    assert ai.state == _idle_state


def test_state_transition_to_chase_when_in_range():
    """MonsterAI transitions to ChaseState when player within 10 tiles."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(6, 6))

    ai = MonsterAI(orc)
    ai._update_state(player)

    assert ai.state == _chase_state


def test_state_transition_to_attack_when_adjacent():
    """MonsterAI transitions to AttackState when adjacent to player."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(10, 11))

    ai = MonsterAI(orc)
    ai._update_state(player)

    assert ai.state == _attack_state


def test_state_transition_to_idle_when_far():
    """MonsterAI transitions to IdleState when player is far away."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(1, 1))  # 18 tiles away

    ai = MonsterAI(orc)
    ai._update_state(player)

    assert ai.state == _idle_state


def test_state_transition_to_idle_when_player_dead():
    """MonsterAI transitions to IdleState when player dies."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    player.take_damage(100)  # Kill player
    orc = create_orc(Position(10, 11))

    ai = MonsterAI(orc)
    ai._update_state(player)

    assert ai.state == _idle_state


def test_state_changes_during_take_turn():
    """State is updated automatically during take_turn."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    player = create_test_player(Position(10, 10))
    orc = create_orc(Position(7, 7))

    ai = MonsterAI(orc)
    # Initially idle
    assert ai.state == _idle_state

    # After take_turn, should be in chase state
    ai.take_turn(player, game_map, [player, orc])
    assert ai.state == _chase_state


def test_singleton_states_are_reused():
    """State instances are singletons (Flyweight pattern)."""
    orc1 = create_orc(Position(5, 5))
    orc2 = create_orc(Position(6, 6))

    ai1 = MonsterAI(orc1)
    ai2 = MonsterAI(orc2)

    # Both should use the same instance
    assert ai1.state is ai2.state
    assert ai1.state is _idle_state
