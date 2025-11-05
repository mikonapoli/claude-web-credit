"""Tests for StatusEffectsComponent."""

from roguelike.components.entity import ComponentEntity
from roguelike.components.status_effects import StatusEffectsComponent, StatusEffect
from roguelike.utils.position import Position


def test_status_effects_component_creation():
    """StatusEffectsComponent can be created."""
    component = StatusEffectsComponent()
    assert component is not None


def test_status_effects_component_starts_empty():
    """StatusEffectsComponent starts with no effects."""
    component = StatusEffectsComponent()
    assert component.get_effect_count() == 0


def test_add_effect_returns_true():
    """Adding an effect with valid duration returns True."""
    component = StatusEffectsComponent()
    result = component.add_effect("poison", duration=5, power=2)
    assert result is True


def test_add_effect_with_zero_duration_returns_false():
    """Adding an effect with zero duration returns False."""
    component = StatusEffectsComponent()
    result = component.add_effect("poison", duration=0, power=2)
    assert result is False


def test_add_effect_with_negative_duration_returns_false():
    """Adding an effect with negative duration returns False."""
    component = StatusEffectsComponent()
    result = component.add_effect("poison", duration=-1, power=2)
    assert result is False


def test_add_effect_increases_count():
    """Adding an effect increases effect count."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    assert component.get_effect_count() == 1


def test_add_multiple_different_effects():
    """Can add multiple different effects."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.add_effect("confusion", duration=3, power=0)
    assert component.get_effect_count() == 2


def test_has_effect_returns_true_when_present():
    """has_effect returns True for active effects."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    assert component.has_effect("poison") is True


def test_has_effect_returns_false_when_not_present():
    """has_effect returns False for inactive effects."""
    component = StatusEffectsComponent()
    assert component.has_effect("poison") is False


def test_get_effect_returns_effect_when_present():
    """get_effect returns StatusEffect when present."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    effect = component.get_effect("poison")
    assert effect is not None


def test_get_effect_returns_none_when_not_present():
    """get_effect returns None when effect not present."""
    component = StatusEffectsComponent()
    effect = component.get_effect("poison")
    assert effect is None


def test_get_effect_has_correct_type():
    """Retrieved effect has correct effect_type."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    effect = component.get_effect("poison")
    assert effect.effect_type == "poison"


def test_get_effect_has_correct_duration():
    """Retrieved effect has correct duration."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    effect = component.get_effect("poison")
    assert effect.duration == 5


def test_get_effect_has_correct_power():
    """Retrieved effect has correct power."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    effect = component.get_effect("poison")
    assert effect.power == 2


def test_get_effect_has_correct_source():
    """Retrieved effect has correct source."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2, source="Snake")
    effect = component.get_effect("poison")
    assert effect.source == "Snake"


def test_remove_effect_returns_true_when_removed():
    """remove_effect returns True when effect exists."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    result = component.remove_effect("poison")
    assert result is True


def test_remove_effect_returns_false_when_not_present():
    """remove_effect returns False when effect doesn't exist."""
    component = StatusEffectsComponent()
    result = component.remove_effect("poison")
    assert result is False


def test_remove_effect_decreases_count():
    """Removing an effect decreases effect count."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.remove_effect("poison")
    assert component.get_effect_count() == 0


def test_remove_effect_removes_effect():
    """Removed effect is no longer active."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.remove_effect("poison")
    assert component.has_effect("poison") is False


def test_get_all_effects_returns_list():
    """get_all_effects returns a list."""
    component = StatusEffectsComponent()
    effects = component.get_all_effects()
    assert isinstance(effects, list)


def test_get_all_effects_returns_empty_when_no_effects():
    """get_all_effects returns empty list when no effects."""
    component = StatusEffectsComponent()
    effects = component.get_all_effects()
    assert len(effects) == 0


def test_get_all_effects_returns_correct_count():
    """get_all_effects returns correct number of effects."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.add_effect("confusion", duration=3, power=0)
    effects = component.get_all_effects()
    assert len(effects) == 2


def test_tick_durations_decreases_duration():
    """tick_durations decreases effect duration by 1."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.tick_durations()
    effect = component.get_effect("poison")
    assert effect.duration == 4


def test_tick_durations_returns_empty_when_no_expiration():
    """tick_durations returns empty list when no effects expire."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    expired = component.tick_durations()
    assert len(expired) == 0


def test_tick_durations_removes_expired_effect():
    """tick_durations removes effects with duration 1."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=1, power=2)
    component.tick_durations()
    assert component.has_effect("poison") is False


def test_tick_durations_returns_expired_effect_type():
    """tick_durations returns list of expired effect types."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=1, power=2)
    expired = component.tick_durations()
    assert "poison" in expired


def test_tick_durations_handles_multiple_expirations():
    """tick_durations can expire multiple effects at once."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=1, power=2)
    component.add_effect("confusion", duration=1, power=0)
    expired = component.tick_durations()
    assert len(expired) == 2


def test_tick_durations_only_expires_at_duration_zero():
    """tick_durations only expires when duration reaches 0 or less."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=2, power=2)
    component.tick_durations()
    assert component.has_effect("poison") is True


def test_clear_all_effects_removes_all():
    """clear_all_effects removes all effects."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.add_effect("confusion", duration=3, power=0)
    component.clear_all_effects()
    assert component.get_effect_count() == 0


def test_add_duplicate_effect_takes_longer_duration():
    """Adding duplicate effect keeps the longer duration."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=3, power=2)
    component.add_effect("poison", duration=5, power=2)
    effect = component.get_effect("poison")
    assert effect.duration == 5


def test_add_duplicate_effect_keeps_existing_when_shorter():
    """Adding duplicate with shorter duration keeps existing."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.add_effect("poison", duration=3, power=2)
    effect = component.get_effect("poison")
    assert effect.duration == 5


def test_add_duplicate_effect_does_not_increase_count():
    """Adding duplicate effect doesn't increase count."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.add_effect("poison", duration=3, power=2)
    assert component.get_effect_count() == 1


def test_add_duplicate_effect_takes_higher_power():
    """Adding duplicate effect takes higher power value."""
    component = StatusEffectsComponent()
    component.add_effect("poison", duration=5, power=2)
    component.add_effect("poison", duration=3, power=4)
    effect = component.get_effect("poison")
    assert effect.power == 4


def test_component_can_be_added_to_entity():
    """StatusEffectsComponent can be added to ComponentEntity."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    component = StatusEffectsComponent()
    entity.add_component(component)
    assert entity.has_component(StatusEffectsComponent)


def test_component_can_be_retrieved_from_entity():
    """StatusEffectsComponent can be retrieved from ComponentEntity."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    component = StatusEffectsComponent()
    entity.add_component(component)
    retrieved = entity.get_component(StatusEffectsComponent)
    assert retrieved is component
