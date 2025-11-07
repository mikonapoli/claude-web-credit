"""Tests for newly implemented item effects."""

import pytest

from roguelike.engine.events import EventBus
from roguelike.entities.item import (
    create_scroll_magic_mapping,
    create_scroll_teleport,
    create_lucky_coin,
    create_banana_peel,
    create_rubber_chicken,
    create_gigantism_potion,
    create_shrinking_potion,
)
from roguelike.components.factories import create_orc
from tests.test_helpers import create_test_player
from roguelike.systems.item_system import ItemSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap
from roguelike.world.fov import FOVMap


def test_magic_mapping_reveals_entire_map():
    """Scroll of Magic Mapping reveals all tiles on the map."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    scroll = create_scroll_magic_mapping(Position(0, 0))

    # Create game map and FOV map
    game_map = GameMap(width=20, height=20)
    fov_map = FOVMap(game_map)

    # Initially, explored should be mostly False
    assert not fov_map.explored.all()

    # Use scroll
    success = item_system.use_item(
        scroll, player, player.inventory, fov_map=fov_map
    )

    assert success is True
    assert fov_map.explored.all()  # All tiles should now be explored


def test_teleport_moves_player_to_valid_location():
    """Scroll of Teleportation teleports player to a valid location."""
    from roguelike.world.tile import Tiles

    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    scroll = create_scroll_teleport(Position(0, 0))

    # Create game map with some walkable tiles
    game_map = GameMap(width=20, height=20)

    # Make some tiles walkable (create a floor area)
    for x in range(5, 15):
        for y in range(5, 15):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    entities = []

    original_pos = player.position

    # Use scroll
    success = item_system.use_item(
        scroll, player, player.inventory, game_map=game_map, entities=entities
    )

    assert success is True
    assert player.position != original_pos  # Player should have moved


def test_lucky_coin_applies_xp_bonus():
    """Lucky Coin grants XP bonus effect."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    coin = create_lucky_coin(Position(0, 0))

    # Use coin
    success = item_system.use_item(coin, player, player.inventory)

    assert success is True
    assert status_system.has_effect(player, "xp_bonus") is True


def test_lucky_coin_increases_xp_gain():
    """Lucky Coin increases XP gained from kills."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)
    combat_system = CombatSystem(event_bus)

    player = create_test_player(Position(5, 5))
    coin = create_lucky_coin(Position(0, 0))

    # Use coin to get XP bonus
    item_system.use_item(coin, player, player.inventory)

    # Award XP with bonus active
    initial_xp = player.xp
    combat_system.award_xp(player, 100)

    # Should get 150 XP (100 + 50% bonus)
    assert player.xp == initial_xp + 150


def test_banana_peel_requires_targeting():
    """Banana Peel requires targeting."""
    peel = create_banana_peel(Position(0, 0))
    assert peel.requires_targeting() is True


def test_banana_peel_confuses_target():
    """Banana Peel confuses target on hit."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    orc = create_orc(Position(7, 7))
    peel = create_banana_peel(Position(0, 0))

    # Use peel on orc
    success = item_system.use_item(peel, player, player.inventory, target=orc)

    assert success is True
    assert status_system.has_effect(orc, "confusion") is True


def test_rubber_chicken_requires_targeting():
    """Rubber Chicken requires targeting."""
    chicken = create_rubber_chicken(Position(0, 0))
    assert chicken.requires_targeting() is True


def test_rubber_chicken_deals_damage():
    """Rubber Chicken deals damage to target."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    orc = create_orc(Position(7, 7))
    chicken = create_rubber_chicken(Position(0, 0))

    initial_hp = orc.hp

    # Use chicken on orc
    success = item_system.use_item(chicken, player, player.inventory, target=orc)

    assert success is True
    assert orc.hp < initial_hp  # Orc should have taken damage


def test_gigantism_potion_applies_temporary_power_boost():
    """Gigantism Potion temporarily increases power."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    potion = create_gigantism_potion(Position(0, 0))

    initial_power = player.power

    # Use potion
    success = item_system.use_item(potion, player, player.inventory)

    assert success is True
    assert status_system.has_effect(player, "gigantism") is True
    assert player.power > initial_power  # Power should be increased


def test_gigantism_potion_power_boost_expires():
    """Gigantism Potion power boost is removed when effect expires."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    potion = create_gigantism_potion(Position(0, 0))

    initial_power = player.power

    # Use potion
    item_system.use_item(potion, player, player.inventory)

    # Manually remove effect to test stat removal
    status_system.remove_effect(player, "gigantism")

    assert player.power == initial_power  # Power should be back to normal


def test_shrinking_potion_applies_temporary_defense_boost():
    """Shrinking Potion temporarily increases defense."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    potion = create_shrinking_potion(Position(0, 0))

    initial_defense = player.defense

    # Use potion
    success = item_system.use_item(potion, player, player.inventory)

    assert success is True
    assert status_system.has_effect(player, "shrinking") is True
    assert player.defense > initial_defense  # Defense should be increased


def test_shrinking_potion_defense_boost_expires():
    """Shrinking Potion defense boost is removed when effect expires."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    potion = create_shrinking_potion(Position(0, 0))

    initial_defense = player.defense

    # Use potion
    item_system.use_item(potion, player, player.inventory)

    # Manually remove effect to test stat removal
    status_system.remove_effect(player, "shrinking")

    assert player.defense == initial_defense  # Defense should be back to normal


def test_gigantism_potion_power_boost_expires_naturally():
    """Gigantism Potion power boost is removed when duration runs out."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = create_test_player(Position(5, 5))
    potion = create_gigantism_potion(Position(0, 0))

    initial_power = player.power

    # Use potion
    item_system.use_item(potion, player, player.inventory)

    # Process effects for 10 turns (duration of gigantism)
    for _ in range(10):
        status_system.process_effects(player)

    # Effect should have expired and power should be back to normal
    assert not status_system.has_effect(player, "gigantism")
    assert player.power == initial_power
