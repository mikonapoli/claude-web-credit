"""Tests for event system."""

from roguelike.engine.events import (
    CombatEvent,
    DeathEvent,
    EventBus,
    LevelUpEvent,
    XPGainEvent,
)


def test_event_bus_creation():
    """EventBus can be created."""
    bus = EventBus()
    assert len(bus.subscribers) == 0


def test_subscribe_to_event():
    """Can subscribe to an event type."""
    bus = EventBus()
    called = []

    def callback(event):
        called.append(event)

    bus.subscribe("test", callback)
    assert "test" in bus.subscribers


def test_emit_event_calls_subscriber():
    """Emitting event calls subscribed callback."""
    bus = EventBus()
    received_events = []

    def callback(event):
        received_events.append(event)

    bus.subscribe("combat", callback)
    event = CombatEvent("Player", "Orc", 5, True)
    bus.emit(event)

    assert len(received_events) == 1


def test_emit_combat_event():
    """Combat event contains correct data."""
    bus = EventBus()
    received_events = []

    bus.subscribe("combat", lambda e: received_events.append(e))
    event = CombatEvent("Player", "Orc", 5, True)
    bus.emit(event)

    assert received_events[0].attacker_name == "Player"


def test_multiple_subscribers():
    """Multiple subscribers receive same event."""
    bus = EventBus()
    calls = []

    bus.subscribe("test", lambda e: calls.append(1))
    bus.subscribe("test", lambda e: calls.append(2))

    event = CombatEvent("A", "B", 1, False)
    event.type = "test"
    bus.emit(event)

    assert len(calls) == 2


def test_emit_without_subscribers():
    """Emitting event without subscribers doesn't crash."""
    bus = EventBus()
    event = CombatEvent("A", "B", 1, False)
    bus.emit(event)  # Should not crash


def test_death_event():
    """Death event contains correct data."""
    event = DeathEvent("Orc", 35, True)
    assert event.entity_name == "Orc"
    assert event.xp_value == 35
    assert event.killed_by_player


def test_level_up_event():
    """Level up event contains correct data."""
    event = LevelUpEvent("Player", 2, {"hp": 20, "power": 1})
    assert event.entity_name == "Player"
    assert event.new_level == 2


def test_xp_gain_event():
    """XP gain event contains correct data."""
    event = XPGainEvent("Player", 35)
    assert event.entity_name == "Player"
    assert event.xp_gained == 35


def test_clear_subscribers():
    """Can clear all subscribers."""
    bus = EventBus()
    bus.subscribe("test", lambda e: None)
    bus.clear()
    assert len(bus.subscribers) == 0
