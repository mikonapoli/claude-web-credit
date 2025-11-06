"""Tests for CombatSystem."""

from roguelike.engine.events import EventBus
from roguelike.entities.monster import create_orc
from roguelike.entities.player import Player
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.utils.position import Position


def test_combat_system_creation():
    """CombatSystem can be created with event bus."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)
    assert system.event_bus == event_bus


def test_resolve_attack_reduces_defender_hp():
    """Resolving attack reduces defender HP."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)

    player = Player(Position(0, 0))
    orc = create_orc(Position(1, 1))
    initial_hp = orc.hp

    system.resolve_attack(player, orc)
    assert orc.hp < initial_hp


def test_resolve_attack_emits_combat_event():
    """Resolving attack emits combat event."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)
    events = []

    event_bus.subscribe("combat", lambda e: events.append(e))

    player = Player(Position(0, 0))
    orc = create_orc(Position(1, 1))

    system.resolve_attack(player, orc)
    assert len(events) == 1


def test_resolve_attack_returns_death_status():
    """Resolve attack returns True if defender died."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)

    player = Player(Position(0, 0))
    orc = create_orc(Position(1, 1))

    # Attack multiple times until orc dies
    died = False
    for _ in range(10):
        died = system.resolve_attack(player, orc)
        if died:
            break

    assert died


def test_handle_death_emits_death_event():
    """Handle death emits death event."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)
    events = []

    event_bus.subscribe("death", lambda e: events.append(e))

    orc = create_orc(Position(1, 1))
    system.handle_death(orc, killed_by_player=True)

    assert len(events) == 1


def test_handle_death_event_contains_xp_value():
    """Death event contains XP value."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)
    events = []

    event_bus.subscribe("death", lambda e: events.append(e))

    orc = create_orc(Position(1, 1))
    system.handle_death(orc, killed_by_player=True)

    assert events[0].xp_value == 35


def test_award_xp_increases_recipient_xp():
    """Awarding XP increases recipient XP."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)

    player = Player(Position(0, 0))
    initial_xp = player.xp

    system.award_xp(player, 50)
    assert player.xp == initial_xp + 50


def test_award_xp_emits_xp_gain_event():
    """Awarding XP emits XP gain event."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)
    events = []

    event_bus.subscribe("xp_gain", lambda e: events.append(e))

    player = Player(Position(0, 0))
    system.award_xp(player, 50)

    assert len(events) == 1


def test_award_xp_triggers_level_up():
    """Awarding enough XP triggers level up."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)

    player = Player(Position(0, 0))
    initial_level = player.level

    # Award enough XP to level up (level 2 requires 400 XP: 100 * 2^2)
    new_level = system.award_xp(player, 400)

    assert new_level == 2
    assert player.level > initial_level


def test_level_up_emits_event():
    """Level up emits level up event."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)
    events = []

    event_bus.subscribe("level_up", lambda e: events.append(e))

    player = Player(Position(0, 0))
    system.award_xp(player, 400)  # Level 2 requires 400 XP

    # Should emit level_up event
    assert len(events) == 1


def test_award_xp_without_level_up_returns_none():
    """Awarding XP without level up returns None."""
    event_bus = EventBus()
    system = CombatSystem(event_bus)

    player = Player(Position(0, 0))
    new_level = system.award_xp(player, 50)

    assert new_level is None


def test_resolve_attack_with_strength_buff_increases_damage():
    """Strength buff increases attack damage."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    combat_system = CombatSystem(event_bus, status_system)

    player = Player(Position(0, 0))
    orc = create_orc(Position(1, 1))
    initial_hp = orc.hp

    # Apply strength buff to player
    status_system.apply_effect(player, "strength", duration=5, power=3)

    combat_system.resolve_attack(player, orc)

    # Damage should be greater than without buff
    damage_dealt = initial_hp - orc.hp
    assert damage_dealt > player.power - orc.defense


def test_resolve_attack_with_defense_buff_reduces_damage():
    """Defense buff reduces damage taken."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    combat_system = CombatSystem(event_bus, status_system)

    player = Player(Position(0, 0))
    orc = create_orc(Position(1, 1))
    initial_player_hp = player.hp

    # Apply defense buff to player
    status_system.apply_effect(player, "defense", duration=5, power=2)

    combat_system.resolve_attack(orc, player)

    # Damage should be less than without buff
    damage_taken = initial_player_hp - player.hp
    expected_damage = max(0, orc.power - player.defense)
    assert damage_taken < expected_damage


def test_resolve_attack_with_gigantism_increases_power_and_defense():
    """Gigantism buff increases both power and defense."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    combat_system = CombatSystem(event_bus, status_system)

    player = Player(Position(0, 0))
    orc = create_orc(Position(1, 1))

    # Apply gigantism buff to player
    status_system.apply_effect(player, "gigantism", duration=5, power=4)

    modifiers = status_system.get_stat_modifiers(player)
    assert modifiers["power"] == 4
    assert modifiers["defense"] == 2
