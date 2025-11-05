"""Tests for SpellComponent."""

import pytest
from roguelike.components.spells import SpellComponent
from roguelike.magic.spell import Spell, SpellSchool, TargetType


@pytest.fixture
def spell_component():
    """Create a spell component for testing."""
    return SpellComponent()


@pytest.fixture
def magic_missile():
    """Create a magic missile spell."""
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
def fireball():
    """Create a fireball spell."""
    return Spell(
        id="fireball",
        name="Fireball",
        school=SpellSchool.EVOCATION,
        mana_cost=15,
        power=25,
        target_type=TargetType.AREA,
        range=8,
        area_radius=2,
    )


@pytest.fixture
def summon_creature():
    """Create a summon spell."""
    return Spell(
        id="summon_creature",
        name="Summon Creature",
        school=SpellSchool.CONJURATION,
        mana_cost=20,
        power=15,
        target_type=TargetType.SINGLE,
        range=3,
    )


def test_spell_component_starts_empty(spell_component):
    """SpellComponent starts with no spells."""
    assert spell_component.spell_count == 0
    assert spell_component.spells == []


def test_learn_spell_adds_spell(spell_component, magic_missile):
    """learn_spell adds a spell to known spells."""
    result = spell_component.learn_spell(magic_missile)
    assert result is True
    assert spell_component.spell_count == 1


def test_learn_spell_returns_false_if_already_known(spell_component, magic_missile):
    """learn_spell returns False if spell already known."""
    spell_component.learn_spell(magic_missile)
    result = spell_component.learn_spell(magic_missile)
    assert result is False
    assert spell_component.spell_count == 1


def test_knows_spell_returns_true_when_known(spell_component, magic_missile):
    """knows_spell returns True for known spells."""
    spell_component.learn_spell(magic_missile)
    assert spell_component.knows_spell("magic_missile") is True


def test_knows_spell_returns_false_when_unknown(spell_component):
    """knows_spell returns False for unknown spells."""
    assert spell_component.knows_spell("fireball") is False


def test_get_spell_returns_spell_when_known(spell_component, magic_missile):
    """get_spell returns spell when known."""
    spell_component.learn_spell(magic_missile)
    spell = spell_component.get_spell("magic_missile")
    assert spell is not None
    assert spell.id == "magic_missile"


def test_get_spell_returns_none_when_unknown(spell_component):
    """get_spell returns None for unknown spells."""
    spell = spell_component.get_spell("unknown_spell")
    assert spell is None


def test_forget_spell_removes_spell(spell_component, magic_missile):
    """forget_spell removes a known spell."""
    spell_component.learn_spell(magic_missile)
    result = spell_component.forget_spell("magic_missile")
    assert result is True
    assert spell_component.spell_count == 0


def test_forget_spell_returns_false_when_unknown(spell_component):
    """forget_spell returns False for unknown spell."""
    result = spell_component.forget_spell("unknown_spell")
    assert result is False


def test_spells_property_returns_all_spells(spell_component, magic_missile, fireball):
    """spells property returns list of all known spells."""
    spell_component.learn_spell(magic_missile)
    spell_component.learn_spell(fireball)
    spells = spell_component.spells
    assert len(spells) == 2
    assert magic_missile in spells
    assert fireball in spells


def test_get_spells_by_school_filters_correctly(
    spell_component, magic_missile, fireball, summon_creature
):
    """get_spells_by_school returns only spells from that school."""
    spell_component.learn_spell(magic_missile)
    spell_component.learn_spell(fireball)
    spell_component.learn_spell(summon_creature)

    evocation_spells = spell_component.get_spells_by_school(SpellSchool.EVOCATION)
    assert len(evocation_spells) == 2
    assert magic_missile in evocation_spells
    assert fireball in evocation_spells

    conjuration_spells = spell_component.get_spells_by_school(SpellSchool.CONJURATION)
    assert len(conjuration_spells) == 1
    assert summon_creature in conjuration_spells


def test_get_spells_by_school_returns_empty_when_none(spell_component, magic_missile):
    """get_spells_by_school returns empty list when no spells match."""
    spell_component.learn_spell(magic_missile)
    spells = spell_component.get_spells_by_school(SpellSchool.TRANSMUTATION)
    assert len(spells) == 0
