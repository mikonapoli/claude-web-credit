"""Tests for SpellLoader."""

import json
import tempfile
from pathlib import Path

import pytest
from roguelike.data.spell_loader import SpellLoader
from roguelike.magic.spell import SpellSchool, TargetType


@pytest.fixture
def spell_data():
    """Sample spell data."""
    return {
        "spells": [
            {
                "id": "magic_missile",
                "name": "Magic Missile",
                "school": "EVOCATION",
                "mana_cost": 5,
                "power": 10,
                "target_type": "SINGLE",
                "range": 5,
                "description": "A dart of magical force",
            },
            {
                "id": "fireball",
                "name": "Fireball",
                "school": "EVOCATION",
                "mana_cost": 15,
                "power": 25,
                "target_type": "AREA",
                "range": 8,
                "area_radius": 2,
                "description": "A massive explosion",
            },
        ]
    }


@pytest.fixture
def temp_spell_file(spell_data):
    """Create temporary spell file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(spell_data, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()


def test_spell_loader_loads_spells(temp_spell_file):
    """SpellLoader loads spells from JSON file."""
    loader = SpellLoader(temp_spell_file)

    assert len(loader.spells) == 2
    assert "magic_missile" in loader.spells
    assert "fireball" in loader.spells


def test_get_spell_returns_spell_when_found(temp_spell_file):
    """get_spell returns spell when found."""
    loader = SpellLoader(temp_spell_file)
    spell = loader.get_spell("magic_missile")

    assert spell is not None
    assert spell.name == "Magic Missile"
    assert spell.school == SpellSchool.EVOCATION


def test_get_spell_returns_none_when_not_found(temp_spell_file):
    """get_spell returns None when spell not found."""
    loader = SpellLoader(temp_spell_file)
    spell = loader.get_spell("nonexistent")

    assert spell is None


def test_get_all_spells_returns_all_spells(temp_spell_file):
    """get_all_spells returns list of all spells."""
    loader = SpellLoader(temp_spell_file)
    spells = loader.get_all_spells()

    assert len(spells) == 2


def test_get_available_spell_ids_returns_ids(temp_spell_file):
    """get_available_spell_ids returns list of spell IDs."""
    loader = SpellLoader(temp_spell_file)
    ids = loader.get_available_spell_ids()

    assert "magic_missile" in ids
    assert "fireball" in ids


def test_spell_loader_parses_spell_properties(temp_spell_file):
    """SpellLoader correctly parses spell properties."""
    loader = SpellLoader(temp_spell_file)
    spell = loader.get_spell("fireball")

    assert spell.id == "fireball"
    assert spell.name == "Fireball"
    assert spell.school == SpellSchool.EVOCATION
    assert spell.mana_cost == 15
    assert spell.power == 25
    assert spell.target_type == TargetType.AREA
    assert spell.range == 8
    assert spell.area_radius == 2


def test_spell_loader_reload(temp_spell_file):
    """reload reloads spells from file."""
    loader = SpellLoader(temp_spell_file)
    initial_count = len(loader.spells)

    # Modify file
    with open(temp_spell_file, "r") as f:
        data = json.load(f)
    data["spells"].append(
        {
            "id": "heal",
            "name": "Heal",
            "school": "TRANSMUTATION",
            "mana_cost": 8,
            "power": 15,
            "target_type": "SELF",
            "range": 0,
        }
    )
    with open(temp_spell_file, "w") as f:
        json.dump(data, f)

    loader.reload()

    assert len(loader.spells) == initial_count + 1
    assert "heal" in loader.spells
