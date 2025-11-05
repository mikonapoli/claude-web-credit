"""Tests for Spell data model."""

import pytest
from roguelike.magic.spell import Spell, SpellSchool, TargetType


def test_spell_creation():
    """Spell can be created with all fields."""
    spell = Spell(
        id="magic_missile",
        name="Magic Missile",
        school=SpellSchool.EVOCATION,
        mana_cost=5,
        power=10,
        target_type=TargetType.SINGLE,
        range=5,
        description="A dart of magical force",
    )
    assert spell.id == "magic_missile"
    assert spell.name == "Magic Missile"
    assert spell.school == SpellSchool.EVOCATION
    assert spell.mana_cost == 5
    assert spell.power == 10
    assert spell.target_type == TargetType.SINGLE
    assert spell.range == 5
    assert spell.area_radius == 0


def test_spell_with_area_radius():
    """Spell can have area_radius for AOE effects."""
    spell = Spell(
        id="fireball",
        name="Fireball",
        school=SpellSchool.EVOCATION,
        mana_cost=15,
        power=25,
        target_type=TargetType.AREA,
        range=8,
        area_radius=2,
    )
    assert spell.area_radius == 2


def test_spell_from_dict():
    """Spell can be created from dictionary."""
    data = {
        "id": "magic_missile",
        "name": "Magic Missile",
        "school": "EVOCATION",
        "mana_cost": 5,
        "power": 10,
        "target_type": "SINGLE",
        "range": 5,
        "description": "A dart of magical force",
    }
    spell = Spell.from_dict(data)
    assert spell.id == "magic_missile"
    assert spell.school == SpellSchool.EVOCATION
    assert spell.target_type == TargetType.SINGLE


def test_spell_from_dict_with_optional_fields():
    """Spell from_dict handles missing optional fields."""
    data = {
        "id": "heal",
        "name": "Heal",
        "school": "TRANSMUTATION",
        "mana_cost": 8,
        "power": 15,
        "target_type": "SELF",
        "range": 0,
    }
    spell = Spell.from_dict(data)
    assert spell.area_radius == 0
    assert spell.description == ""


def test_spell_to_dict():
    """Spell can be converted to dictionary."""
    spell = Spell(
        id="magic_missile",
        name="Magic Missile",
        school=SpellSchool.EVOCATION,
        mana_cost=5,
        power=10,
        target_type=TargetType.SINGLE,
        range=5,
        description="A dart of magical force",
    )
    data = spell.to_dict()
    assert data["id"] == "magic_missile"
    assert data["school"] == "EVOCATION"
    assert data["target_type"] == "SINGLE"


def test_spell_post_init_converts_string_school():
    """Spell __post_init__ converts string school to enum."""
    spell = Spell(
        id="test",
        name="Test",
        school="CONJURATION",  # type: ignore
        mana_cost=5,
        power=10,
        target_type=TargetType.SELF,
        range=0,
    )
    assert spell.school == SpellSchool.CONJURATION


def test_spell_post_init_converts_string_target():
    """Spell __post_init__ converts string target_type to enum."""
    spell = Spell(
        id="test",
        name="Test",
        school=SpellSchool.EVOCATION,
        mana_cost=5,
        power=10,
        target_type="BEAM",  # type: ignore
        range=5,
    )
    assert spell.target_type == TargetType.BEAM


def test_spell_schools_exist():
    """All spell schools are defined."""
    assert SpellSchool.EVOCATION
    assert SpellSchool.CONJURATION
    assert SpellSchool.TRANSMUTATION


def test_target_types_exist():
    """All target types are defined."""
    assert TargetType.SELF
    assert TargetType.SINGLE
    assert TargetType.AREA
    assert TargetType.BEAM
