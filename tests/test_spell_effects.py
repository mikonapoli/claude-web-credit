"""Tests for spell effects."""

import pytest
from tests.test_helpers import create_test_entity
from roguelike.magic.effects import BuffEffect, DamageEffect, EffectResult, HealEffect
from roguelike.utils.position import Position


@pytest.fixture
def caster():
    """Create a caster actor."""
    return create_test_entity(
        Position(0, 0),
        "@",
        "Wizard",
        max_hp=50,
        defense=2,
        power=5,
    )


@pytest.fixture
def target():
    """Create a target actor."""
    return create_test_entity(
        Position(1, 1),
        "o",
        "Orc",
        max_hp=20,
        defense=1,
        power=3,
    )


def test_damage_effect_deals_damage(caster, target):
    """DamageEffect reduces target HP."""
    effect = DamageEffect()
    initial_hp = target.hp

    result = effect.apply(caster, target, power=10)

    assert result.success is True
    assert result.damage_dealt == 10
    assert target.hp == initial_hp - 10


def test_damage_effect_can_kill_target(caster, target):
    """DamageEffect can kill target."""
    effect = DamageEffect()
    result = effect.apply(caster, target, power=100)

    assert result.target_died is True
    assert target.is_alive is False


def test_damage_effect_message_on_kill(caster, target):
    """DamageEffect shows kill message when target dies."""
    effect = DamageEffect()
    result = effect.apply(caster, target, power=100)

    assert "kills" in result.message.lower()
    assert caster.name in result.message


def test_damage_effect_message_on_hit(caster, target):
    """DamageEffect shows hit message when target survives."""
    effect = DamageEffect()
    result = effect.apply(caster, target, power=5)

    assert "hits" in result.message.lower()
    assert "damage" in result.message.lower()
    assert str(result.damage_dealt) in result.message


def test_heal_effect_restores_hp(caster, target):
    """HealEffect restores HP."""
    target.take_damage(10)
    effect = HealEffect()

    result = effect.apply(caster, target, power=5)

    assert result.success is True
    assert result.healing_done == 5


def test_heal_effect_cannot_overheal(caster, target):
    """HealEffect cannot exceed max HP."""
    target.take_damage(5)
    effect = HealEffect()

    result = effect.apply(caster, target, power=100)

    assert result.healing_done == 5
    assert target.hp == target.max_hp


def test_heal_effect_fails_when_already_full(caster, target):
    """HealEffect returns success=False when target at full HP."""
    effect = HealEffect()
    result = effect.apply(caster, target, power=10)

    assert result.success is False
    assert result.healing_done == 0


def test_heal_effect_message_when_healing(caster, target):
    """HealEffect shows healing message."""
    target.take_damage(10)
    effect = HealEffect()
    result = effect.apply(caster, target, power=5)

    assert "heal" in result.message.lower()
    assert str(result.healing_done) in result.message


def test_heal_effect_message_when_self_healing(caster):
    """HealEffect shows self-healing message."""
    caster.take_damage(10)
    effect = HealEffect()
    result = effect.apply(caster, caster, power=5)

    assert caster.name in result.message
    assert result.healing_done == 5


def test_heal_effect_message_when_already_full(caster, target):
    """HealEffect shows 'already at full health' message."""
    effect = HealEffect()
    result = effect.apply(caster, target, power=10)

    assert "already" in result.message.lower()
    assert "full" in result.message.lower()


def test_buff_effect_increases_power(caster, target):
    """BuffEffect increases target power."""
    effect = BuffEffect(buff_amount=3)
    initial_power = target.power

    result = effect.apply(caster, target, power=10)

    assert result.success is True
    assert target.power == initial_power + 3


def test_buff_effect_message(caster, target):
    """BuffEffect shows buff message."""
    effect = BuffEffect(buff_amount=2)
    result = effect.apply(caster, target, power=10)

    assert "empower" in result.message.lower()
    assert "+2" in result.message


def test_buff_effect_self_buff_message(caster):
    """BuffEffect shows self-buff message."""
    effect = BuffEffect(buff_amount=2)
    result = effect.apply(caster, caster, power=10)

    assert "empowered" in result.message.lower()
    assert caster.name in result.message


def test_effect_result_has_required_fields():
    """EffectResult has all required fields."""
    result = EffectResult(success=True, message="Test")

    assert result.success is True
    assert result.message == "Test"
    assert result.damage_dealt == 0
    assert result.healing_done == 0
    assert result.target_died is False
