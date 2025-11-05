"""Tests for crafting component."""

import pytest

from roguelike.components.crafting import CraftingComponent


def test_crafting_component_creation():
    """CraftingComponent can be created with tags."""
    tags = {"herbal", "magical"}
    component = CraftingComponent(tags=tags)
    assert component.tags == tags
    assert component.consumable is True
    assert component.craftable is False


def test_crafting_component_has_tag():
    """CraftingComponent can check for single tag."""
    component = CraftingComponent(tags={"herbal", "magical"})
    assert component.has_tag("herbal") is True


def test_crafting_component_does_not_have_tag():
    """CraftingComponent returns False for missing tag."""
    component = CraftingComponent(tags={"herbal"})
    assert component.has_tag("magical") is False


def test_crafting_component_has_all_tags():
    """CraftingComponent can check for multiple tags."""
    component = CraftingComponent(tags={"herbal", "magical", "rare"})
    assert component.has_all_tags({"herbal", "magical"}) is True


def test_crafting_component_does_not_have_all_tags():
    """CraftingComponent returns False when missing some tags."""
    component = CraftingComponent(tags={"herbal"})
    assert component.has_all_tags({"herbal", "magical"}) is False


def test_crafting_component_has_any_tag():
    """CraftingComponent returns True if has any of the tags."""
    component = CraftingComponent(tags={"herbal", "magical"})
    assert component.has_any_tag({"herbal", "metallic"}) is True


def test_crafting_component_does_not_have_any_tag():
    """CraftingComponent returns False if has none of the tags."""
    component = CraftingComponent(tags={"herbal"})
    assert component.has_any_tag({"magical", "metallic"}) is False


def test_crafting_component_non_consumable():
    """CraftingComponent can be marked as non-consumable."""
    component = CraftingComponent(tags={"tool"}, consumable=False)
    assert component.consumable is False


def test_crafting_component_craftable():
    """CraftingComponent can be marked as craftable."""
    component = CraftingComponent(tags={"magical"}, craftable=True)
    assert component.craftable is True
