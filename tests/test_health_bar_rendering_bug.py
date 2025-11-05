"""Test to demonstrate health bar rendering bug with non-Actor entities."""

import pytest

from roguelike.entities.item import create_healing_potion
from roguelike.entities.monster import Monster, create_orc
from roguelike.entities.player import Player
from roguelike.utils.position import Position


class TestHealthBarRenderingBug:
    """Tests for health bar rendering with mixed entity types."""

    def test_item_does_not_have_health_attributes(self):
        """Items do not have hp, max_hp, or is_alive attributes."""
        item = create_healing_potion(Position(5, 5))

        # Items should not have health attributes
        assert not hasattr(item, "hp")
        assert not hasattr(item, "max_hp")

    def test_living_entities_list_includes_items(self):
        """The living_entities filter includes items which lack health."""
        # Create a mix of entities
        player = Player(position=Position(10, 10))
        monster = create_orc(position=Position(15, 15))
        dead_monster = create_orc(position=Position(20, 20))
        dead_monster.hp = 0
        item = create_healing_potion(Position(12, 12))

        entities = [monster, dead_monster, item]

        # This is the current filter logic from game_engine.py
        living_entities = [e for e in entities if not isinstance(e, Monster) or e.is_alive]

        # The bug: living_entities includes the item (because it's not a Monster)
        assert item in living_entities
        # And the item lacks health attributes
        assert not hasattr(item, "hp")

    def test_item_lacks_required_attributes_for_health_bar(self):
        """Items lack the attributes needed for health bar rendering."""
        item = create_healing_potion(Position(10, 10))

        # These are the attributes accessed by render_health_bar
        with pytest.raises(AttributeError):
            _ = item.hp

        with pytest.raises(AttributeError):
            _ = item.max_hp

        with pytest.raises(AttributeError):
            _ = item.is_alive
