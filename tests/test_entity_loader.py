"""Tests for data-driven entity loading."""

import json
import tempfile
from pathlib import Path

import pytest

from roguelike.components.combat import CombatComponent
from roguelike.components.crafting import CraftingComponent
from roguelike.components.health import HealthComponent
from roguelike.components.level import LevelComponent
from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
from roguelike.data.entity_loader import EntityLoader
from roguelike.utils.position import Position


def test_entity_loader_creation():
    """EntityLoader can be created."""
    loader = EntityLoader()
    assert loader.templates is not None


def test_entity_loader_has_default_templates():
    """EntityLoader loads default templates."""
    loader = EntityLoader()
    available_types = loader.get_available_types()

    assert "player" in available_types
    assert "orc" in available_types
    assert "troll" in available_types


def test_create_player_from_template():
    """Can create player entity from template."""
    loader = EntityLoader()
    player = loader.create_entity("player", Position(10, 10))

    assert player.name == "Player"
    assert player.char == "@"
    assert player.position == Position(10, 10)
    assert player.blocks_movement


def test_player_has_components():
    """Player created from template has all components."""
    loader = EntityLoader()
    player = loader.create_entity("player", Position(10, 10))

    assert player.has_component(HealthComponent)
    assert player.has_component(CombatComponent)
    assert player.has_component(LevelComponent)


def test_player_health_component():
    """Player health component has correct values."""
    loader = EntityLoader()
    player = loader.create_entity("player", Position(10, 10))

    health = player.get_component(HealthComponent)
    assert health.max_hp == 30
    assert health.hp == 30


def test_player_combat_component():
    """Player combat component has correct values."""
    loader = EntityLoader()
    player = loader.create_entity("player", Position(10, 10))

    combat = player.get_component(CombatComponent)
    assert combat.power == 5
    assert combat.defense == 2


def test_player_level_component():
    """Player level component has correct values."""
    loader = EntityLoader()
    player = loader.create_entity("player", Position(10, 10))

    level = player.get_component(LevelComponent)
    assert level.level == 1
    assert level.xp == 0
    assert level.xp_value == 0


def test_create_orc_from_template():
    """Can create orc entity from template."""
    loader = EntityLoader()
    orc = loader.create_entity("orc", Position(5, 5))

    assert orc.name == "Orc"
    assert orc.char == "o"
    assert orc.position == Position(5, 5)


def test_orc_has_correct_stats():
    """Orc created from template has correct stats."""
    loader = EntityLoader()
    orc = loader.create_entity("orc", Position(5, 5))

    health = orc.get_component(HealthComponent)
    combat = orc.get_component(CombatComponent)
    level = orc.get_component(LevelComponent)

    assert health.max_hp == 10
    assert combat.power == 3
    assert combat.defense == 0
    assert level.xp_value == 35


def test_create_troll_from_template():
    """Can create troll entity from template."""
    loader = EntityLoader()
    troll = loader.create_entity("troll", Position(5, 5))

    assert troll.name == "Troll"
    assert troll.char == "T"


def test_troll_has_correct_stats():
    """Troll created from template has correct stats."""
    loader = EntityLoader()
    troll = loader.create_entity("troll", Position(5, 5))

    health = troll.get_component(HealthComponent)
    combat = troll.get_component(CombatComponent)
    level = troll.get_component(LevelComponent)

    assert health.max_hp == 16
    assert combat.power == 4
    assert combat.defense == 1
    assert level.xp_value == 100


def test_create_invalid_entity_type():
    """Creating invalid entity type raises KeyError."""
    loader = EntityLoader()

    with pytest.raises(KeyError):
        loader.create_entity("invalid_type", Position(0, 0))


def test_entity_loader_with_custom_path():
    """EntityLoader can load from custom path."""
    # Create temporary JSON file
    custom_data = {
        "test_entity": {
            "char": "T",
            "name": "Test",
            "blocks_movement": False,
            "components": {
                "health": {"max_hp": 50},
                "combat": {"power": 10, "defense": 5},
            },
        }
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(custom_data, f)
        temp_path = Path(f.name)

    try:
        loader = EntityLoader(temp_path)
        entity = loader.create_entity("test_entity", Position(0, 0))

        assert entity.name == "Test"
        health = entity.get_component(HealthComponent)
        assert health.max_hp == 50
    finally:
        temp_path.unlink()


def test_entity_loader_reload():
    """EntityLoader can reload templates."""
    loader = EntityLoader()
    initial_types = loader.get_available_types()

    loader.reload()
    reloaded_types = loader.get_available_types()

    assert initial_types == reloaded_types


def test_multiple_entities_same_position():
    """Can create multiple entities at same position."""
    loader = EntityLoader()
    pos = Position(5, 5)

    orc1 = loader.create_entity("orc", pos)
    orc2 = loader.create_entity("orc", pos)

    assert orc1 is not orc2
    assert orc1.position == orc2.position


def test_entity_independence():
    """Entities created from same template are independent."""
    loader = EntityLoader()

    orc1 = loader.create_entity("orc", Position(5, 5))
    orc2 = loader.create_entity("orc", Position(10, 10))

    # Damage one orc
    health1 = orc1.get_component(HealthComponent)
    health2 = orc2.get_component(HealthComponent)

    health1.take_damage(5)

    assert health1.hp == 5
    assert health2.hp == 10  # Should be unaffected


def test_create_crafting_item_from_template():
    """Can create crafting item from template."""
    loader = EntityLoader()
    moonleaf = loader.create_entity("moonleaf", Position(5, 5))

    assert moonleaf.name == "Moonleaf"
    assert moonleaf.char == "%"
    assert not moonleaf.blocks_movement


def test_crafting_item_has_crafting_component():
    """Crafting item has CraftingComponent."""
    loader = EntityLoader()
    moonleaf = loader.create_entity("moonleaf", Position(5, 5))

    assert moonleaf.has_component(CraftingComponent)


def test_crafting_component_has_correct_tags():
    """CraftingComponent has tags from template."""
    loader = EntityLoader()
    moonleaf = loader.create_entity("moonleaf", Position(5, 5))

    crafting = moonleaf.get_component(CraftingComponent)
    assert crafting.has_tag("herbal")
    assert crafting.has_tag("verdant")


def test_crafting_item_consumable_flag():
    """Crafting item has correct consumable flag."""
    loader = EntityLoader()
    moonleaf = loader.create_entity("moonleaf", Position(5, 5))

    crafting = moonleaf.get_component(CraftingComponent)
    assert crafting.consumable is True


def test_crafting_item_craftable_flag():
    """Crafting item has correct craftable flag."""
    loader = EntityLoader()
    moonleaf = loader.create_entity("moonleaf", Position(5, 5))

    crafting = moonleaf.get_component(CraftingComponent)
    assert crafting.craftable is False


def test_multiple_crafting_items_with_different_tags():
    """Different crafting items have different tags."""
    loader = EntityLoader()
    moonleaf = loader.create_entity("moonleaf", Position(5, 5))
    crystal = loader.create_entity("mana_crystal", Position(6, 6))

    moonleaf_crafting = moonleaf.get_component(CraftingComponent)
    crystal_crafting = crystal.get_component(CraftingComponent)

    assert moonleaf_crafting.has_tag("herbal")
    assert not moonleaf_crafting.has_tag("magical")
    assert crystal_crafting.has_tag("magical")
    assert not crystal_crafting.has_tag("herbal")

def test_entity_loader_can_load_recipe_discovery_component():
    """EntityLoader can load RecipeDiscoveryComponent from template."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "test_player": {
                    "char": "@",
                    "name": "Test Player",
                    "blocks_movement": True,
                    "components": {
                        "recipe_discovery": {}
                    }
                }
            },
            f,
        )
        temp_path = f.name

    loader = EntityLoader(data_path=temp_path)
    player = loader.create_entity("test_player", Position(5, 5))

    assert player.has_component(RecipeDiscoveryComponent)
    Path(temp_path).unlink()


def test_recipe_discovery_component_starts_empty():
    """RecipeDiscoveryComponent loaded from template starts empty."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "test_player": {
                    "char": "@",
                    "name": "Test Player",
                    "blocks_movement": True,
                    "components": {
                        "recipe_discovery": {}
                    }
                }
            },
            f,
        )
        temp_path = f.name

    loader = EntityLoader(data_path=temp_path)
    player = loader.create_entity("test_player", Position(5, 5))

    discovery = player.get_component(RecipeDiscoveryComponent)
    assert discovery.get_discovery_count() == 0
    Path(temp_path).unlink()
