"""Tests for StatusEffectsSystem."""

from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.status_effects import StatusEffectsComponent
from roguelike.engine.events import (
    EventBus,
    StatusEffectAppliedEvent,
    StatusEffectExpiredEvent,
    StatusEffectTickEvent,
)
from tests.test_helpers import create_test_entity, create_test_player, create_test_monster
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.utils.position import Position


def test_status_effects_system_creation():
    """StatusEffectsSystem can be created."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    assert system is not None


def test_apply_effect_to_component_entity_adds_component():
    """Applying effect to ComponentEntity adds StatusEffectsComponent."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)

    assert entity.has_component(StatusEffectsComponent)


def test_apply_effect_to_component_entity_returns_true():
    """apply_effect returns True for valid ComponentEntity."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    result = system.apply_effect(entity, "poison", duration=5, power=2)

    assert result is True


def test_apply_effect_to_component_entity_adds_effect():
    """Applying effect to ComponentEntity adds the effect."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)

    status = entity.get_component(StatusEffectsComponent)
    assert status.has_effect("poison")


def test_apply_effect_to_actor_returns_true():
    """apply_effect returns True for valid Actor."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    actor = Actor(Position(5, 5), "o", "Orc", max_hp=10, defense=0, power=3)

    result = system.apply_effect(actor, "poison", duration=5, power=2)

    assert result is True


def test_apply_effect_to_actor_stores_effects():
    """Applying effect to Actor stores effects internally."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    actor = Actor(Position(5, 5), "o", "Orc", max_hp=10, defense=0, power=3)

    system.apply_effect(actor, "poison", duration=5, power=2)

    assert hasattr(actor, "_status_effects")


def test_apply_effect_emits_applied_event():
    """apply_effect emits StatusEffectAppliedEvent."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    events = []
    event_bus.subscribe("status_effect_applied", lambda e: events.append(e))

    system.apply_effect(entity, "poison", duration=5, power=2)

    assert len(events) == 1


def test_applied_event_has_correct_entity_name():
    """StatusEffectAppliedEvent has correct entity name."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    events = []
    event_bus.subscribe("status_effect_applied", lambda e: events.append(e))

    system.apply_effect(entity, "poison", duration=5, power=2)

    assert events[0].entity_name == "Player"


def test_applied_event_has_correct_effect_type():
    """StatusEffectAppliedEvent has correct effect type."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    events = []
    event_bus.subscribe("status_effect_applied", lambda e: events.append(e))

    system.apply_effect(entity, "poison", duration=5, power=2)

    assert events[0].effect_type == "poison"


def test_applied_event_has_correct_duration():
    """StatusEffectAppliedEvent has correct duration."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    events = []
    event_bus.subscribe("status_effect_applied", lambda e: events.append(e))

    system.apply_effect(entity, "poison", duration=5, power=2)

    assert events[0].duration == 5


def test_has_effect_returns_true_for_component_entity():
    """has_effect returns True for ComponentEntity with effect."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)

    assert system.has_effect(entity, "poison") is True


def test_has_effect_returns_false_for_component_entity_without_effect():
    """has_effect returns False for ComponentEntity without effect."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    assert system.has_effect(entity, "poison") is False


def test_has_effect_returns_true_for_actor():
    """has_effect returns True for Actor with effect."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    actor = Actor(Position(5, 5), "o", "Orc", max_hp=10, defense=0, power=3)

    system.apply_effect(actor, "poison", duration=5, power=2)

    assert system.has_effect(actor, "poison") is True


def test_has_effect_returns_false_for_actor_without_effect():
    """has_effect returns False for Actor without effect."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    actor = Actor(Position(5, 5), "o", "Orc", max_hp=10, defense=0, power=3)

    assert system.has_effect(actor, "poison") is False


def test_process_effects_emits_tick_events():
    """process_effects emits StatusEffectTickEvent."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)

    events = []
    event_bus.subscribe("status_effect_tick", lambda e: events.append(e))

    system.process_effects(entity)

    assert len(events) == 1


def test_tick_event_has_correct_effect_type():
    """StatusEffectTickEvent has correct effect type."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)

    events = []
    event_bus.subscribe("status_effect_tick", lambda e: events.append(e))

    system.process_effects(entity)

    assert events[0].effect_type == "poison"


def test_process_effects_decrements_duration():
    """process_effects decrements effect duration."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)
    system.process_effects(entity)

    status = entity.get_component(StatusEffectsComponent)
    effect = status.get_effect("poison")
    assert effect.duration == 4


def test_process_effects_removes_expired_effects():
    """process_effects removes effects at duration 0."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=1, power=2)
    system.process_effects(entity)

    assert system.has_effect(entity, "poison") is False


def test_process_effects_emits_expired_event():
    """process_effects emits StatusEffectExpiredEvent."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=1, power=2)

    events = []
    event_bus.subscribe("status_effect_expired", lambda e: events.append(e))

    system.process_effects(entity)

    assert len(events) == 1


def test_expired_event_has_correct_effect_type():
    """StatusEffectExpiredEvent has correct effect type."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=1, power=2)

    events = []
    event_bus.subscribe("status_effect_expired", lambda e: events.append(e))

    system.process_effects(entity)

    assert events[0].effect_type == "poison"


def test_process_poison_damages_component_entity():
    """Poison effect damages ComponentEntity with HealthComponent."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    entity.add_component(health)

    system.apply_effect(entity, "poison", duration=5, power=2)
    system.process_effects(entity)

    assert health.hp == 28


def test_process_poison_damages_actor():
    """Poison effect damages Actor."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    actor = Actor(Position(5, 5), "o", "Orc", max_hp=10, defense=0, power=3)

    system.apply_effect(actor, "poison", duration=5, power=2)
    system.process_effects(actor)

    assert actor.hp == 8


def test_process_confusion_does_not_damage():
    """Confusion effect does not deal damage."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    entity.add_component(health)

    system.apply_effect(entity, "confusion", duration=5, power=0)
    system.process_effects(entity)

    assert health.hp == 30


def test_process_invisibility_does_not_damage():
    """Invisibility effect does not deal damage."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    entity.add_component(health)

    system.apply_effect(entity, "invisibility", duration=5, power=0)
    system.process_effects(entity)

    assert health.hp == 30


def test_remove_effect_removes_effect_from_component_entity():
    """remove_effect removes effect from ComponentEntity."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)
    system.remove_effect(entity, "poison")

    assert system.has_effect(entity, "poison") is False


def test_remove_effect_returns_true_when_removed():
    """remove_effect returns True when effect exists."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)
    result = system.remove_effect(entity, "poison")

    assert result is True


def test_remove_effect_returns_false_when_not_present():
    """remove_effect returns False when effect doesn't exist."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    result = system.remove_effect(entity, "poison")

    assert result is False


def test_remove_effect_emits_expired_event():
    """remove_effect emits StatusEffectExpiredEvent."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)

    events = []
    event_bus.subscribe("status_effect_expired", lambda e: events.append(e))

    system.remove_effect(entity, "poison")

    assert len(events) == 1


def test_get_effect_display_returns_empty_for_no_effects():
    """get_effect_display returns empty list when no effects."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    display = system.get_effect_display(entity)

    assert len(display) == 0


def test_get_effect_display_returns_effect_string():
    """get_effect_display returns formatted effect string."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)

    display = system.get_effect_display(entity)

    assert "Poison (5)" in display


def test_get_effect_display_returns_multiple_effects():
    """get_effect_display returns all active effects."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    system.apply_effect(entity, "poison", duration=5, power=2)
    system.apply_effect(entity, "confusion", duration=3, power=0)

    display = system.get_effect_display(entity)

    assert len(display) == 2


def test_process_effects_handles_entity_without_effects():
    """process_effects handles entity without StatusEffectsComponent."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    entity = ComponentEntity(Position(5, 5), "@", "Player")

    # Should not raise error
    system.process_effects(entity)

    assert True


def test_process_effects_works_on_actor():
    """process_effects works on Actor entities."""
    event_bus = EventBus()
    system = StatusEffectsSystem(event_bus)
    actor = Actor(Position(5, 5), "o", "Orc", max_hp=10, defense=0, power=3)

    system.apply_effect(actor, "poison", duration=5, power=2)

    events = []
    event_bus.subscribe("status_effect_tick", lambda e: events.append(e))

    system.process_effects(actor)

    assert len(events) == 1
