"""Tests for item system."""

import pytest

from roguelike.engine.events import EventBus, HealingEvent, ItemUseEvent
from roguelike.entities.actor import Actor
from roguelike.entities.item import (
    create_banana_peel,
    create_cheese_wheel,
    create_coffee,
    create_cursed_ring,
    create_gigantism_potion,
    create_greater_healing_potion,
    create_healing_potion,
    create_lucky_coin,
    create_rubber_chicken,
    create_scroll_magic_mapping,
    create_scroll_teleport,
    create_shrinking_potion,
    create_strength_potion,
)
from roguelike.systems.inventory import Inventory
from roguelike.systems.item_system import ItemSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


@pytest.fixture
def event_bus():
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def status_effects_system(event_bus):
    """Create a status effects system for testing."""
    return StatusEffectsSystem(event_bus)


@pytest.fixture
def item_system(event_bus, status_effects_system):
    """Create an item system for testing."""
    return ItemSystem(event_bus, status_effects_system)


@pytest.fixture
def game_map():
    """Create a test game map."""
    return GameMap(width=20, height=20)


@pytest.fixture
def fov_map(game_map):
    """Create a test FOV map."""
    return FOVMap(game_map)


@pytest.fixture
def player():
    """Create a test player."""
    return Actor(
        position=Position(5, 5),
        char="@",
        name="Player",
        max_hp=30,
        defense=2,
        power=5,
    )


@pytest.fixture
def inventory():
    """Create an inventory for testing."""
    return Inventory(capacity=10)


def test_healing_potion_heals_player(item_system, player, inventory):
    """Healing potion restores HP."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert player.hp == 30


def test_healing_potion_removed_from_inventory(item_system, player, inventory):
    """Healing potion is removed after use."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert len(inventory) == 0


def test_healing_potion_at_full_hp_not_used(item_system, player, inventory):
    """Healing potion cannot be used at full HP."""
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    result = item_system.use_item(potion, player, inventory)

    assert result is False


def test_healing_potion_at_full_hp_not_removed(item_system, player, inventory):
    """Healing potion stays in inventory if not used."""
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert len(inventory) == 1


def test_healing_potion_emits_item_use_event(item_system, player, inventory, event_bus):
    """Using healing potion emits item use event."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("item_use", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert len(events) == 1


def test_healing_potion_emits_healing_event(item_system, player, inventory, event_bus):
    """Using healing potion emits healing event."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("healing", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert len(events) == 1


def test_healing_event_has_correct_amount(item_system, player, inventory, event_bus):
    """Healing event contains correct healing amount."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("healing", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert events[0].amount_healed == 20


def test_greater_healing_potion_heals_more(item_system, player, inventory):
    """Greater healing potion restores more HP."""
    player.hp = 10
    potion = create_greater_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert player.hp == 30


def test_cheese_wheel_heals_large_amount(item_system, player, inventory):
    """Cheese wheel restores large amount of HP."""
    player.hp = 1
    cheese = create_cheese_wheel(Position(5, 5))
    inventory.add(cheese)

    item_system.use_item(cheese, player, inventory)

    assert player.hp == 30


def test_healing_capped_at_max_hp(item_system, player, inventory):
    """Healing cannot exceed max HP."""
    player.hp = 25
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert player.hp == 30


def test_strength_potion_increases_power(item_system, player, inventory):
    """Strength potion increases power."""
    initial_power = player.power
    potion = create_strength_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert player.power == initial_power + 3


def test_strength_potion_removed_after_use(item_system, player, inventory):
    """Strength potion is removed after use."""
    potion = create_strength_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert len(inventory) == 0


def test_use_item_returns_true_on_success(item_system, player, inventory):
    """use_item returns True when item is used successfully."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    result = item_system.use_item(potion, player, inventory)

    assert result is True


def test_item_use_event_has_correct_item_name(item_system, player, inventory, event_bus):
    """Item use event contains correct item name."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("item_use", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert events[0].item_name == "Healing Potion"


def test_item_use_event_has_correct_user_name(item_system, player, inventory, event_bus):
    """Item use event contains correct user name."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("item_use", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert events[0].entity_name == "Player"


def test_healing_event_has_correct_entity_name(item_system, player, inventory, event_bus):
    """Healing event contains correct entity name."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("healing", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert events[0].entity_name == "Player"


# Tests for new item effects


def test_scroll_magic_mapping_reveals_entire_map(item_system, player, inventory, game_map, fov_map):
    """Magic mapping scroll reveals the entire map."""
    scroll = create_scroll_magic_mapping(Position(5, 5))
    inventory.add(scroll)

    # Initially, map should not be fully explored
    assert not fov_map.explored.all()

    item_system.use_item(scroll, player, inventory, fov_map=fov_map)

    # After using scroll, entire map should be explored
    assert fov_map.explored.all()


def test_scroll_magic_mapping_removed_from_inventory(item_system, player, inventory, fov_map):
    """Magic mapping scroll is removed after use."""
    scroll = create_scroll_magic_mapping(Position(5, 5))
    inventory.add(scroll)

    item_system.use_item(scroll, player, inventory, fov_map=fov_map)

    assert len(inventory) == 0


def test_scroll_teleport_changes_player_position(item_system, player, inventory, game_map):
    """Teleportation scroll changes player position."""
    scroll = create_scroll_teleport(Position(5, 5))
    inventory.add(scroll)
    original_position = player.position

    # Make at least one tile walkable
    from roguelike.world.tile import Tiles
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)

    item_system.use_item(scroll, player, inventory, game_map=game_map)

    # Player should be at a different position
    assert player.position != original_position or game_map.is_walkable(player.position)


def test_scroll_teleport_removed_from_inventory(item_system, player, inventory, game_map):
    """Teleportation scroll is removed after use."""
    scroll = create_scroll_teleport(Position(5, 5))
    inventory.add(scroll)

    # Make at least one tile walkable
    from roguelike.world.tile import Tiles
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)

    item_system.use_item(scroll, player, inventory, game_map=game_map)

    assert len(inventory) == 0


def test_gigantism_potion_applies_status_effect(item_system, player, inventory, status_effects_system):
    """Gigantism potion applies gigantism status effect."""
    potion = create_gigantism_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert status_effects_system.has_effect(player, "gigantism")


def test_gigantism_potion_removed_from_inventory(item_system, player, inventory):
    """Gigantism potion is removed after use."""
    potion = create_gigantism_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert len(inventory) == 0


def test_shrinking_potion_applies_status_effect(item_system, player, inventory, status_effects_system):
    """Shrinking potion applies shrinking status effect."""
    potion = create_shrinking_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert status_effects_system.has_effect(player, "shrinking")


def test_shrinking_potion_removed_from_inventory(item_system, player, inventory):
    """Shrinking potion is removed after use."""
    potion = create_shrinking_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert len(inventory) == 0


def test_coffee_applies_speed_status_effect(item_system, player, inventory, status_effects_system):
    """Coffee applies speed status effect."""
    coffee = create_coffee(Position(5, 5))
    inventory.add(coffee)

    item_system.use_item(coffee, player, inventory)

    assert status_effects_system.has_effect(player, "speed")


def test_coffee_removed_from_inventory(item_system, player, inventory):
    """Coffee is removed after use."""
    coffee = create_coffee(Position(5, 5))
    inventory.add(coffee)

    item_system.use_item(coffee, player, inventory)

    assert len(inventory) == 0


def test_lucky_coin_applies_lucky_status_effect(item_system, player, inventory, status_effects_system):
    """Lucky coin applies lucky status effect."""
    coin = create_lucky_coin(Position(5, 5))
    inventory.add(coin)

    item_system.use_item(coin, player, inventory)

    assert status_effects_system.has_effect(player, "lucky")


def test_lucky_coin_removed_from_inventory(item_system, player, inventory):
    """Lucky coin is removed after use."""
    coin = create_lucky_coin(Position(5, 5))
    inventory.add(coin)

    item_system.use_item(coin, player, inventory)

    assert len(inventory) == 0


def test_banana_peel_applies_confusion_status_effect(item_system, player, inventory, status_effects_system):
    """Banana peel applies confusion status effect."""
    peel = create_banana_peel(Position(5, 5))
    inventory.add(peel)

    item_system.use_item(peel, player, inventory)

    assert status_effects_system.has_effect(player, "confusion")


def test_banana_peel_removed_from_inventory(item_system, player, inventory):
    """Banana peel is removed after use."""
    peel = create_banana_peel(Position(5, 5))
    inventory.add(peel)

    item_system.use_item(peel, player, inventory)

    assert len(inventory) == 0


def test_rubber_chicken_applies_status_effect(item_system, player, inventory, status_effects_system):
    """Rubber chicken applies rubber_chicken status effect."""
    chicken = create_rubber_chicken(Position(5, 5))
    inventory.add(chicken)

    item_system.use_item(chicken, player, inventory)

    assert status_effects_system.has_effect(player, "rubber_chicken")


def test_rubber_chicken_removed_from_inventory(item_system, player, inventory):
    """Rubber chicken is removed after use."""
    chicken = create_rubber_chicken(Position(5, 5))
    inventory.add(chicken)

    item_system.use_item(chicken, player, inventory)

    assert len(inventory) == 0
