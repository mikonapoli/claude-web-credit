"""Tests for MagicSystem."""

import pytest
from roguelike.components.mana import ManaComponent
from roguelike.components.spells import SpellComponent
from roguelike.engine.events import EventBus
from tests.test_helpers import create_test_entity
from roguelike.magic.effects import DamageEffect, HealEffect
from roguelike.magic.spell import Spell, SpellSchool, TargetType
from roguelike.systems.magic_system import MagicSystem
from roguelike.utils.position import Position


@pytest.fixture
def event_bus():
    """Create event bus for testing."""
    return EventBus()


@pytest.fixture
def magic_system(event_bus):
    """Create magic system for testing."""
    return MagicSystem(event_bus)


@pytest.fixture
def wizard():
    """Create wizard actor."""
    return Actor(
        position=Position(0, 0),
        char="@",
        name="Wizard",
        max_hp=50,
        defense=2,
        power=5,
    )


@pytest.fixture
def orc():
    """Create orc actor."""
    return Actor(
        position=Position(1, 1),
        char="o",
        name="Orc",
        max_hp=20,
        defense=1,
        power=3,
    )


@pytest.fixture
def magic_missile():
    """Create magic missile spell."""
    return Spell(
        id="magic_missile",
        name="Magic Missile",
        school=SpellSchool.EVOCATION,
        mana_cost=5,
        power=10,
        target_type=TargetType.SINGLE,
        range=5,
    )


@pytest.fixture
def heal_spell():
    """Create heal spell."""
    return Spell(
        id="heal",
        name="Heal",
        school=SpellSchool.TRANSMUTATION,
        mana_cost=8,
        power=15,
        target_type=TargetType.SELF,
        range=0,
    )


def test_register_spell_effect(magic_system, magic_missile):
    """register_spell_effect adds effect to system."""
    effect = DamageEffect()
    magic_system.register_spell_effect(magic_missile.id, effect)

    assert magic_missile.id in magic_system._spell_effects


def test_can_cast_spell_when_valid(magic_system, wizard, magic_missile):
    """can_cast_spell returns True when all conditions met."""
    mana = ManaComponent(max_mp=50)
    spells = SpellComponent()
    spells.learn_spell(magic_missile)
    magic_system.register_spell_effect(magic_missile.id, DamageEffect())

    can_cast, reason = magic_system.can_cast_spell(wizard, magic_missile, mana, spells)

    assert can_cast is True
    assert reason == ""


def test_can_cast_spell_fails_when_dead(magic_system, wizard, magic_missile):
    """can_cast_spell returns False when caster is dead."""
    wizard.take_damage(100)
    mana = ManaComponent(max_mp=50)

    can_cast, reason = magic_system.can_cast_spell(wizard, magic_missile, mana)

    assert can_cast is False
    assert "dead" in reason.lower()


def test_can_cast_spell_fails_without_mana(magic_system, wizard, magic_missile):
    """can_cast_spell returns False when insufficient mana."""
    mana = ManaComponent(max_mp=50)
    mana.consume_mana(48)  # Leave only 2 MP
    magic_system.register_spell_effect(magic_missile.id, DamageEffect())

    can_cast, reason = magic_system.can_cast_spell(wizard, magic_missile, mana)

    assert can_cast is False
    assert "mana" in reason.lower()


def test_can_cast_spell_fails_without_knowing_spell(
    magic_system, wizard, magic_missile
):
    """can_cast_spell returns False when spell not known."""
    mana = ManaComponent(max_mp=50)
    spells = SpellComponent()
    # Don't learn the spell
    magic_system.register_spell_effect(magic_missile.id, DamageEffect())

    can_cast, reason = magic_system.can_cast_spell(wizard, magic_missile, mana, spells)

    assert can_cast is False
    assert "doesn't know" in reason.lower()


def test_can_cast_spell_fails_without_effect(magic_system, wizard, magic_missile):
    """can_cast_spell returns False when spell has no effect."""
    mana = ManaComponent(max_mp=50)
    spells = SpellComponent()
    spells.learn_spell(magic_missile)
    # Don't register effect

    can_cast, reason = magic_system.can_cast_spell(wizard, magic_missile, mana, spells)

    assert can_cast is False
    assert "no effect" in reason.lower()


def test_cast_spell_consumes_mana(magic_system, wizard, orc, magic_missile):
    """cast_spell consumes mana from caster."""
    mana = ManaComponent(max_mp=50)
    spells = SpellComponent()
    spells.learn_spell(magic_missile)
    magic_system.register_spell_effect(magic_missile.id, DamageEffect())

    result = magic_system.cast_spell(wizard, orc, magic_missile, mana, spells)

    assert result.success is True
    assert mana.mp == 45  # 50 - 5


def test_cast_spell_applies_effect(magic_system, wizard, orc, magic_missile):
    """cast_spell applies spell effect to target."""
    mana = ManaComponent(max_mp=50)
    spells = SpellComponent()
    spells.learn_spell(magic_missile)
    magic_system.register_spell_effect(magic_missile.id, DamageEffect())
    initial_hp = orc.hp

    result = magic_system.cast_spell(wizard, orc, magic_missile, mana, spells)

    assert result.success is True
    assert result.damage_dealt == 10
    assert orc.hp == initial_hp - 10


def test_cast_spell_emits_events(magic_system, event_bus, wizard, orc, magic_missile):
    """cast_spell emits spell cast and mana changed events."""
    mana = ManaComponent(max_mp=50)
    spells = SpellComponent()
    spells.learn_spell(magic_missile)
    magic_system.register_spell_effect(magic_missile.id, DamageEffect())

    spell_events = []
    mana_events = []
    event_bus.subscribe("spell_cast", lambda e: spell_events.append(e))
    event_bus.subscribe("mana_changed", lambda e: mana_events.append(e))

    magic_system.cast_spell(wizard, orc, magic_missile, mana, spells)

    assert len(spell_events) == 1
    assert len(mana_events) == 1
    assert spell_events[0].spell_name == "Magic Missile"
    assert mana_events[0].new_mp == 45


def test_cast_spell_fails_when_cannot_cast(magic_system, wizard, orc, magic_missile):
    """cast_spell returns failure when conditions not met."""
    mana = ManaComponent(max_mp=50)
    mana.consume_mana(48)  # Not enough mana
    magic_system.register_spell_effect(magic_missile.id, DamageEffect())

    result = magic_system.cast_spell(wizard, orc, magic_missile, mana)

    assert result.success is False


def test_cast_spell_works_without_mana_component(
    magic_system, wizard, orc, magic_missile
):
    """cast_spell works when no mana component provided."""
    magic_system.register_spell_effect(magic_missile.id, DamageEffect())

    result = magic_system.cast_spell(wizard, orc, magic_missile)

    assert result.success is True


def test_regenerate_mana_increases_mp(magic_system, wizard):
    """regenerate_mana restores mana."""
    mana = ManaComponent(max_mp=50, mp_regen_rate=3)
    mana.consume_mana(20)

    regenerated = magic_system.regenerate_mana(wizard.name, mana)

    assert regenerated == 3
    assert mana.mp == 33


def test_regenerate_mana_emits_event(magic_system, event_bus, wizard):
    """regenerate_mana emits mana changed event."""
    mana = ManaComponent(max_mp=50, mp_regen_rate=3)
    mana.consume_mana(20)

    events = []
    event_bus.subscribe("mana_changed", lambda e: events.append(e))

    magic_system.regenerate_mana(wizard.name, mana)

    assert len(events) == 1
    assert events[0].new_mp == 33


def test_regenerate_mana_no_event_when_full(magic_system, event_bus, wizard):
    """regenerate_mana doesn't emit event when already full."""
    mana = ManaComponent(max_mp=50, mp_regen_rate=3)

    events = []
    event_bus.subscribe("mana_changed", lambda e: events.append(e))

    magic_system.regenerate_mana(wizard.name, mana)

    assert len(events) == 0
