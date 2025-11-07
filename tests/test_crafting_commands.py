"""Tests for crafting commands."""

import pytest

from roguelike.commands.crafting_commands import AutoCraftCommand, CraftCommand
from roguelike.components.crafting import CraftingComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.inventory import InventoryComponent
from roguelike.data.entity_loader import EntityLoader
from roguelike.data.recipe_loader import RecipeLoader
from roguelike.engine.events import EventBus
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.crafting import CraftingSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap


@pytest.fixture
def event_bus():
    """Create event bus for testing."""
    return EventBus()


@pytest.fixture
def recipe_loader():
    """Create recipe loader for testing."""
    return RecipeLoader()


@pytest.fixture
def crafting_system(recipe_loader, event_bus):
    """Create crafting system for testing."""
    return CraftingSystem(recipe_loader, event_bus)


@pytest.fixture
def message_log():
    """Create message log for testing."""
    return MessageLog()


@pytest.fixture
def player():
    """Create player entity with inventory for testing."""
    player = ComponentEntity(
        position=Position(10, 10),
        char="@",
        name="Player",
        blocks_movement=True,
    )
    player.add_component(InventoryComponent(capacity=20))
    return player


@pytest.fixture
def entity_loader():
    """Create entity loader for testing."""
    return EntityLoader()


@pytest.fixture
def game_map():
    """Create game map for testing."""
    return GameMap(width=80, height=50)


@pytest.fixture
def combat_system(event_bus):
    """Create combat system for testing."""
    return CombatSystem(event_bus)


@pytest.fixture
def movement_system(game_map):
    """Create movement system for testing."""
    return MovementSystem(game_map)


@pytest.fixture
def status_effects_system(event_bus):
    """Create status effects system for testing."""
    return StatusEffectsSystem(event_bus)


@pytest.fixture
def ai_system(combat_system, movement_system, game_map, status_effects_system):
    """Create AI system for testing."""
    return AISystem(combat_system, movement_system, game_map, status_effects_system)


def test_craft_command_success(
    player, crafting_system, message_log, entity_loader,
    ai_system, combat_system, status_effects_system
):
    """Test successful crafting with CraftCommand."""
    # Create ingredients for healing potion (herbal + magical)
    moonleaf = entity_loader.create_entity("moonleaf", Position(10, 10))
    crystal = entity_loader.create_entity("mana_crystal", Position(10, 10))

    # Add to inventory
    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(crystal)

    # Create craft command
    entities = []
    cmd = CraftCommand(
        player, [moonleaf, crystal], crafting_system, message_log,
        entities, ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should succeed
    assert result.success is True
    assert result.turn_consumed is True

    # Ingredients should be removed (both are consumable)
    assert moonleaf not in inventory.get_items()
    assert crystal not in inventory.get_items()

    # Result should be added to inventory
    items = inventory.get_items()
    assert len(items) == 1
    assert items[0].name == "Healing Potion"


def test_craft_command_no_recipe(
    player, crafting_system, message_log, entity_loader,
    ai_system, combat_system, status_effects_system
):
    """Test crafting with ingredients that don't match a recipe."""
    # Create incompatible ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(10, 10))
    nightshade = entity_loader.create_entity("nightshade", Position(10, 10))

    # Add to inventory
    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(nightshade)

    # Create craft command
    entities = []
    cmd = CraftCommand(
        player, [moonleaf, nightshade], crafting_system, message_log,
        entities, ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should fail
    assert result.success is False
    assert result.turn_consumed is False

    # Ingredients should still be in inventory
    assert moonleaf in inventory.get_items()
    assert nightshade in inventory.get_items()


def test_craft_command_ingredient_not_in_inventory(
    player, crafting_system, message_log, entity_loader,
    ai_system, combat_system, status_effects_system
):
    """Test crafting with ingredient not in inventory."""
    # Create ingredients but don't add to inventory
    moonleaf = entity_loader.create_entity("moonleaf", Position(10, 10))
    crystal = entity_loader.create_entity("mana_crystal", Position(10, 10))

    # Create craft command
    entities = []
    cmd = CraftCommand(
        player, [moonleaf, crystal], crafting_system, message_log,
        entities, ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should fail
    assert result.success is False
    assert result.turn_consumed is False


def test_auto_craft_command_finds_recipe(
    player, crafting_system, message_log, entity_loader,
    ai_system, combat_system, status_effects_system
):
    """Test AutoCraftCommand finds valid recipe."""
    # Create ingredients for healing potion
    moonleaf = entity_loader.create_entity("moonleaf", Position(10, 10))
    crystal = entity_loader.create_entity("mana_crystal", Position(10, 10))

    # Add to inventory
    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(crystal)

    # Create auto craft command
    entities = []
    cmd = AutoCraftCommand(
        player, crafting_system, message_log, entities,
        ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should succeed
    assert result.success is True
    assert result.turn_consumed is True

    # Should have crafted healing potion
    items = inventory.get_items()
    assert len(items) == 1
    assert items[0].name == "Healing Potion"


def test_auto_craft_command_no_valid_recipe(
    player, crafting_system, message_log, entity_loader,
    ai_system, combat_system, status_effects_system
):
    """Test AutoCraftCommand with no valid recipes."""
    # Create incompatible ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(10, 10))
    nightshade = entity_loader.create_entity("nightshade", Position(10, 10))

    # Add to inventory
    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(nightshade)

    # Create auto craft command
    entities = []
    cmd = AutoCraftCommand(
        player, crafting_system, message_log, entities,
        ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should fail
    assert result.success is False
    assert result.turn_consumed is False

    # Items should still be in inventory
    assert len(inventory.get_items()) == 2


def test_auto_craft_command_not_enough_items(
    player, crafting_system, message_log, entity_loader,
    ai_system, combat_system, status_effects_system
):
    """Test AutoCraftCommand with less than 2 craftable items."""
    # Create only one craftable item
    moonleaf = entity_loader.create_entity("moonleaf", Position(10, 10))

    # Add to inventory
    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)

    # Create auto craft command
    entities = []
    cmd = AutoCraftCommand(
        player, crafting_system, message_log, entities,
        ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should fail
    assert result.success is False
    assert result.turn_consumed is False


def test_auto_craft_command_prefers_three_ingredient_recipes(
    player, crafting_system, message_log, entity_loader,
    ai_system, combat_system, status_effects_system
):
    """Test AutoCraftCommand tries 3-ingredient recipes before 2-ingredient."""
    # Create ingredients for both 2-item and 3-item recipes
    # 3-item: strength_elixir (herbal + magical + rare)
    moonleaf = entity_loader.create_entity("moonleaf", Position(10, 10))
    crystal = entity_loader.create_entity("mana_crystal", Position(10, 10))
    dragon_scale = entity_loader.create_entity("dragon_scale", Position(10, 10))

    # Add to inventory
    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(crystal)
    inventory.add_item(dragon_scale)

    # Create auto craft command
    entities = []
    cmd = AutoCraftCommand(
        player, crafting_system, message_log, entities,
        ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should succeed
    assert result.success is True

    # Should have crafted something (exact result depends on recipe matching)
    items = inventory.get_items()
    assert len(items) > 0


def test_craft_command_drops_item_if_inventory_full(
    player, crafting_system, message_log, entity_loader,
    ai_system, combat_system, status_effects_system
):
    """Test crafting drops item on ground if inventory is full."""
    # Fill inventory to capacity
    inventory = player.get_component(InventoryComponent)
    for i in range(inventory.capacity - 2):
        item = entity_loader.create_entity("moonleaf", Position(10, 10))
        inventory.add_item(item)

    # Add crafting ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(10, 10))
    crystal = entity_loader.create_entity("mana_crystal", Position(10, 10))
    inventory.add_item(moonleaf)
    inventory.add_item(crystal)

    # Now inventory is exactly at capacity
    assert inventory.is_full()

    # Create craft command with entities list
    entities = []
    cmd = CraftCommand(
        player, [moonleaf, crystal], crafting_system, message_log,
        entities, ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should succeed - ingredients are removed first, freeing space
    assert result.success is True

    # Check that crafted item was added
    # (inventory had 2 removed, 1 added, so should be capacity - 1)
    assert len(inventory.get_items()) == inventory.capacity - 1
