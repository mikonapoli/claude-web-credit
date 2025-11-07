"""Integration tests for item buff effects in combat and XP systems."""

import pytest

from roguelike.engine.events import EventBus
from roguelike.entities.actor import Actor
from roguelike.entities.item import (
    create_gigantism_potion,
    create_lucky_coin,
    create_rubber_chicken,
    create_shrinking_potion,
)
from roguelike.systems.combat import calculate_damage
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.inventory import Inventory
from roguelike.systems.item_system import ItemSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.utils.position import Position


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
def combat_system(event_bus):
    """Create a combat system for testing."""
    return CombatSystem(event_bus)


@pytest.fixture
def player():
    """Create a test player with base stats."""
    return Actor(
        position=Position(5, 5),
        char="@",
        name="Player",
        max_hp=30,
        defense=2,
        power=5,
    )


@pytest.fixture
def enemy():
    """Create a test enemy with base stats."""
    return Actor(
        position=Position(10, 10),
        char="o",
        name="Orc",
        max_hp=20,
        defense=1,
        power=4,
    )


@pytest.fixture
def inventory():
    """Create an inventory for testing."""
    return Inventory(capacity=10)


def test_gigantism_potion_increases_combat_damage(item_system, player, enemy, inventory):
    """Gigantism potion increases damage dealt in combat."""
    # Baseline damage: player power (5) - enemy defense (1) = 4 damage
    baseline_damage = calculate_damage(player, enemy)
    assert baseline_damage == 4

    # Use gigantism potion
    potion = create_gigantism_potion(Position(5, 5))
    inventory.add(potion)
    item_system.use_item(potion, player, inventory)

    # With gigantism (+3 power): effective power (8) - enemy defense (1) = 7 damage
    buffed_damage = calculate_damage(player, enemy)
    assert buffed_damage == 7


def test_rubber_chicken_increases_combat_damage(item_system, player, enemy, inventory):
    """Rubber chicken increases damage dealt in combat."""
    # Baseline damage: player power (5) - enemy defense (1) = 4 damage
    baseline_damage = calculate_damage(player, enemy)
    assert baseline_damage == 4

    # Use rubber chicken
    chicken = create_rubber_chicken(Position(5, 5))
    inventory.add(chicken)
    item_system.use_item(chicken, player, inventory)

    # With rubber chicken (+1 power): effective power (6) - enemy defense (1) = 5 damage
    buffed_damage = calculate_damage(player, enemy)
    assert buffed_damage == 5


def test_shrinking_potion_increases_defense(item_system, player, enemy, inventory):
    """Shrinking potion increases defense, reducing damage taken."""
    # Baseline damage taken: enemy power (4) - player defense (2) = 2 damage
    baseline_damage = calculate_damage(enemy, player)
    assert baseline_damage == 2

    # Use shrinking potion
    potion = create_shrinking_potion(Position(5, 5))
    inventory.add(potion)
    item_system.use_item(potion, player, inventory)

    # With shrinking (+2 defense): enemy power (4) - effective defense (4) = 0 damage
    buffed_damage = calculate_damage(enemy, player)
    assert buffed_damage == 0


def test_multiple_buffs_stack(item_system, player, enemy, inventory):
    """Multiple power buffs stack correctly."""
    # Baseline damage: player power (5) - enemy defense (1) = 4 damage
    baseline_damage = calculate_damage(player, enemy)
    assert baseline_damage == 4

    # Use both gigantism and rubber chicken
    gigantism = create_gigantism_potion(Position(5, 5))
    chicken = create_rubber_chicken(Position(6, 6))
    inventory.add(gigantism)
    inventory.add(chicken)
    item_system.use_item(gigantism, player, inventory)
    item_system.use_item(chicken, player, inventory)

    # With gigantism (+3) and rubber chicken (+1): effective power (9) - enemy defense (1) = 8 damage
    buffed_damage = calculate_damage(player, enemy)
    assert buffed_damage == 8


def test_lucky_coin_increases_xp_gain(combat_system, item_system, player, inventory):
    """Lucky coin increases XP gained by 50%."""
    # Baseline XP gain
    base_xp = 100
    combat_system.award_xp(player, base_xp)
    assert player.xp == 100

    # Reset XP
    player.xp = 0

    # Use lucky coin (50% bonus)
    coin = create_lucky_coin(Position(5, 5))
    inventory.add(coin)
    item_system.use_item(coin, player, inventory)

    # Award XP with lucky buff: 100 + (100 * 50 / 100) = 150 XP
    combat_system.award_xp(player, base_xp)
    assert player.xp == 150


def test_lucky_coin_xp_bonus_rounds_down(combat_system, item_system, player, inventory):
    """Lucky coin XP bonus uses integer division."""
    # Use lucky coin
    coin = create_lucky_coin(Position(5, 5))
    inventory.add(coin)
    item_system.use_item(coin, player, inventory)

    # Award odd XP amount: 15 + (15 * 50 / 100) = 15 + 7.5 -> 15 + 7 = 22
    combat_system.award_xp(player, 15)
    assert player.xp == 22


def test_buffs_dont_affect_unbuffed_entities(item_system, player, enemy, inventory):
    """Enemy damage is not affected by player's defensive buffs."""
    # Player uses gigantism (affects their damage)
    gigantism = create_gigantism_potion(Position(5, 5))
    inventory.add(gigantism)
    item_system.use_item(gigantism, player, inventory)

    # Enemy attacks player - should not be affected by player's power buff
    # Enemy power (4) - player defense (2) = 2 damage
    damage_to_player = calculate_damage(enemy, player)
    assert damage_to_player == 2


def test_shrinking_only_affects_holder(item_system, player, enemy, inventory):
    """Shrinking buff only affects the entity that drank it."""
    # Player uses shrinking
    shrinking = create_shrinking_potion(Position(5, 5))
    inventory.add(shrinking)
    item_system.use_item(shrinking, player, inventory)

    # Player attacks enemy - shrinking shouldn't affect offense
    # Player power (5) - enemy defense (1) = 4 damage
    player_damage = calculate_damage(player, enemy)
    assert player_damage == 4

    # Enemy attacks player - player's defense should be buffed
    # Enemy power (4) - player effective defense (4) = 0 damage
    enemy_damage = calculate_damage(enemy, player)
    assert enemy_damage == 0
