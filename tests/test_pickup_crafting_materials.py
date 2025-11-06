"""Tests for picking up crafting materials (ComponentEntity items)."""

import pytest

from roguelike.data.entity_loader import EntityLoader
from roguelike.engine.events import EventBus
from roguelike.entities.player import Player
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.turn_manager import TurnManager
from roguelike.ui.input_handler import Action
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


@pytest.fixture
def game_map():
    """Create a test game map."""
    return GameMap(width=20, height=20)


@pytest.fixture
def event_bus():
    """Create event bus."""
    return EventBus()


@pytest.fixture
def player():
    """Create test player."""
    return Player(position=Position(5, 5))


@pytest.fixture
def entity_loader():
    """Create entity loader."""
    return EntityLoader()


@pytest.fixture
def turn_manager(game_map, event_bus):
    """Create turn manager with pickup support."""
    combat_system = CombatSystem(event_bus)
    movement_system = MovementSystem(game_map)
    ai_system = AISystem(combat_system, movement_system, game_map)
    return TurnManager(
        combat_system, movement_system, ai_system, event_bus=event_bus
    )


def test_pickup_crafting_material_moonleaf(player, entity_loader, turn_manager, game_map):
    """Player can pick up moonleaf (ComponentEntity crafting material)."""
    # Create moonleaf at player's position
    moonleaf = entity_loader.create_entity("moonleaf", player.position)
    entities = [moonleaf]

    # Player inventory should be empty
    assert len(player.inventory.items) == 0

    # Try to pick up
    fov_map = FOVMap(game_map)
    turn_consumed, should_quit = turn_manager.handle_player_action(
        Action.PICKUP, player, entities, game_map, fov_map, 8
    )

    # Pickup should succeed
    assert turn_consumed
    assert not should_quit

    # Moonleaf should be in inventory
    assert len(player.inventory.items) == 1
    assert player.inventory.items[0] == moonleaf

    # Moonleaf should be removed from world
    assert moonleaf not in entities


def test_pickup_multiple_crafting_materials(player, entity_loader, turn_manager, game_map):
    """Player can pick up multiple crafting materials."""
    # Create materials at player's position
    moonleaf = entity_loader.create_entity("moonleaf", player.position)
    crystal = entity_loader.create_entity("mana_crystal", Position(6, 5))
    salt = entity_loader.create_entity("purifying_salt", Position(7, 5))

    entities = [moonleaf, crystal, salt]
    fov_map = FOVMap(game_map)

    # Pick up moonleaf at (5, 5)
    turn_consumed, _ = turn_manager.handle_player_action(
        Action.PICKUP, player, entities, game_map, fov_map, 8
    )
    assert turn_consumed
    assert len(player.inventory.items) == 1

    # Move to (6, 5) and pick up crystal
    player.move_to(Position(6, 5))
    turn_consumed, _ = turn_manager.handle_player_action(
        Action.PICKUP, player, entities, game_map, fov_map, 8
    )
    assert turn_consumed
    assert len(player.inventory.items) == 2

    # Move to (7, 5) and pick up salt
    player.move_to(Position(7, 5))
    turn_consumed, _ = turn_manager.handle_player_action(
        Action.PICKUP, player, entities, game_map, fov_map, 8
    )
    assert turn_consumed
    assert len(player.inventory.items) == 3

    # Verify all materials are in inventory
    inventory_names = [item.name for item in player.inventory.items]
    assert "Moonleaf" in inventory_names
    assert "Mana Crystal" in inventory_names
    assert "Purifying Salt" in inventory_names


def test_pickup_fails_when_no_item_at_position(player, turn_manager, game_map):
    """Pickup fails when no item at player's position."""
    entities = []
    fov_map = FOVMap(game_map)

    # Try to pick up with no items
    turn_consumed, should_quit = turn_manager.handle_player_action(
        Action.PICKUP, player, entities, game_map, fov_map, 8
    )

    # Pickup should fail
    assert not turn_consumed
    assert not should_quit
    assert len(player.inventory.items) == 0


def test_pickup_fails_when_inventory_full(player, entity_loader, turn_manager, game_map):
    """Pickup fails when inventory is full."""
    # Fill inventory to capacity
    for i in range(player.inventory.capacity):
        item = entity_loader.create_entity("moonleaf", Position(0, 0))
        player.inventory.add(item)

    # Create item at player's position
    moonleaf = entity_loader.create_entity("moonleaf", player.position)
    entities = [moonleaf]
    fov_map = FOVMap(game_map)

    # Try to pick up with full inventory
    turn_consumed, should_quit = turn_manager.handle_player_action(
        Action.PICKUP, player, entities, game_map, fov_map, 8
    )

    # Pickup should fail
    assert not turn_consumed
    assert not should_quit

    # Item should still be on ground
    assert moonleaf in entities


def test_pickup_emits_event(player, entity_loader, turn_manager, game_map, event_bus):
    """Pickup emits ItemPickupEvent."""
    events_received = []

    def event_handler(event):
        events_received.append(event)

    event_bus.subscribe("item_pickup", event_handler)

    # Create and pick up item
    moonleaf = entity_loader.create_entity("moonleaf", player.position)
    entities = [moonleaf]
    fov_map = FOVMap(game_map)

    turn_manager.handle_player_action(
        Action.PICKUP, player, entities, game_map, fov_map, 8
    )

    # Should have received pickup event
    assert len(events_received) == 1
    event = events_received[0]
    assert event.entity_name == "Player"
    assert event.item_name == "Moonleaf"


def test_all_crafting_materials_can_be_picked_up(player, entity_loader, turn_manager, game_map):
    """All crafting materials can be picked up."""
    materials = [
        "moonleaf",
        "mana_crystal",
        "nightshade",
        "purifying_salt",
        "iron_ore",
        "volcanic_ash",
        "sulfur",
        "frost_essence",
        "dragon_scale",
        "runic_essence",
        "ancient_parchment",
        "phoenix_feather",
        "thunder_stone",
        "shadow_ink",
        "blessed_water",
        "giants_tears",
        "pixie_dust",
    ]

    fov_map = FOVMap(game_map)

    for material_type in materials:
        # Create material at player position
        material = entity_loader.create_entity(material_type, player.position)
        entities = [material]

        # Try to pick up
        turn_consumed, _ = turn_manager.handle_player_action(
            Action.PICKUP, player, entities, game_map, fov_map, 8
        )

        # Should succeed
        assert turn_consumed, f"Failed to pick up {material_type}"
        assert material not in entities, f"{material_type} still in world"
        assert material in player.inventory.items, f"{material_type} not in inventory"

        # Clear inventory for next test
        player.inventory.items.clear()
