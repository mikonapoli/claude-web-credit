"""Tests for crafting events."""

import pytest

from roguelike.engine.events import (
    CraftingAttemptEvent,
    EventBus,
    RecipeDiscoveredEvent,
)


def test_crafting_attempt_event_creation():
    """CraftingAttemptEvent can be created."""
    event = CraftingAttemptEvent(
        crafter_name="Player",
        ingredient_names=["Herb", "Crystal"],
        success=True,
        result_name="Healing Potion",
    )
    assert event.type == "crafting_attempt"
    assert event.crafter_name == "Player"
    assert event.ingredient_names == ["Herb", "Crystal"]
    assert event.success is True
    assert event.result_name == "Healing Potion"


def test_crafting_attempt_event_failed():
    """CraftingAttemptEvent can represent failed crafting."""
    event = CraftingAttemptEvent(
        crafter_name="Player",
        ingredient_names=["Herb", "Metal"],
        success=False,
        result_name=None,
    )
    assert event.success is False
    assert event.result_name is None


def test_recipe_discovered_event_creation():
    """RecipeDiscoveredEvent can be created."""
    event = RecipeDiscoveredEvent(
        recipe_id="healing_potion",
        recipe_name="Healing Potion",
        discoverer_name="Player",
    )
    assert event.type == "recipe_discovered"
    assert event.recipe_id == "healing_potion"
    assert event.recipe_name == "Healing Potion"
    assert event.discoverer_name == "Player"


def test_crafting_attempt_event_emitted():
    """CraftingAttemptEvent can be emitted via EventBus."""
    bus = EventBus()
    received_events = []

    def handler(event):
        received_events.append(event)

    bus.subscribe("crafting_attempt", handler)

    event = CraftingAttemptEvent(
        crafter_name="Player",
        ingredient_names=["Herb"],
        success=True,
        result_name="Potion",
    )
    bus.emit(event)

    assert len(received_events) == 1
    assert received_events[0].crafter_name == "Player"


def test_recipe_discovered_event_emitted():
    """RecipeDiscoveredEvent can be emitted via EventBus."""
    bus = EventBus()
    received_events = []

    def handler(event):
        received_events.append(event)

    bus.subscribe("recipe_discovered", handler)

    event = RecipeDiscoveredEvent(
        recipe_id="test",
        recipe_name="Test Recipe",
        discoverer_name="Player",
    )
    bus.emit(event)

    assert len(received_events) == 1
    assert received_events[0].recipe_id == "test"
