"""Tests for equipment system."""

import pytest

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent, EquipmentSlot, EquipmentStats
from roguelike.components.health import HealthComponent
from roguelike.engine.events import EquipEvent, EventBus, UnequipEvent
from roguelike.systems.equipment_system import EquipmentSystem
from roguelike.utils.position import Position


@pytest.fixture
def event_bus():
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def equipment_system(event_bus):
    """Create an equipment system for testing."""
    return EquipmentSystem(event_bus)


@pytest.fixture
def player_entity():
    """Create a player entity with all necessary components."""
    entity = ComponentEntity(
        position=Position(5, 5),
        char="@",
        name="Player",
        blocks_movement=True,
    )
    # Add components
    entity.add_component(EquipmentComponent())
    entity.add_component(CombatComponent(power=5, defense=2))
    entity.add_component(HealthComponent(max_hp=30))
    return entity


@pytest.fixture
def iron_sword():
    """Create an iron sword item."""
    sword = ComponentEntity(
        position=Position(0, 0),
        char="/",
        name="Iron Sword",
        blocks_movement=False,
    )
    equipment_stats = EquipmentStats(
        slot=EquipmentSlot.WEAPON,
        power_bonus=3,
        defense_bonus=0,
    )
    sword.add_component(equipment_stats)
    return sword


@pytest.fixture
def steel_sword():
    """Create a steel sword item."""
    sword = ComponentEntity(
        position=Position(0, 0),
        char="/",
        name="Steel Sword",
        blocks_movement=False,
    )
    equipment_stats = EquipmentStats(
        slot=EquipmentSlot.WEAPON,
        power_bonus=5,
        defense_bonus=0,
    )
    sword.add_component(equipment_stats)
    return sword


@pytest.fixture
def leather_armor():
    """Create leather armor item."""
    armor = ComponentEntity(
        position=Position(0, 0),
        char="[",
        name="Leather Armor",
        blocks_movement=False,
    )
    equipment_stats = EquipmentStats(
        slot=EquipmentSlot.ARMOR,
        power_bonus=0,
        defense_bonus=2,
    )
    armor.add_component(equipment_stats)
    return armor


@pytest.fixture
def steel_helmet():
    """Create steel helmet item."""
    helmet = ComponentEntity(
        position=Position(0, 0),
        char="^",
        name="Steel Helmet",
        blocks_movement=False,
    )
    equipment_stats = EquipmentStats(
        slot=EquipmentSlot.HELMET,
        power_bonus=0,
        defense_bonus=1,
        max_hp_bonus=5,
    )
    helmet.add_component(equipment_stats)
    return helmet


def test_equip_weapon_increases_power(equipment_system, player_entity, iron_sword):
    """Equipping weapon increases entity power."""
    combat = player_entity.get_component(CombatComponent)
    initial_power = combat.power
    equipment_system.equip_item(player_entity, iron_sword)
    assert combat.power == initial_power + 3


def test_equip_armor_increases_defense(equipment_system, player_entity, leather_armor):
    """Equipping armor increases entity defense."""
    combat = player_entity.get_component(CombatComponent)
    initial_defense = combat.defense
    equipment_system.equip_item(player_entity, leather_armor)
    assert combat.defense == initial_defense + 2


def test_equip_helmet_increases_max_hp(equipment_system, player_entity, steel_helmet):
    """Equipping helmet increases max HP."""
    health = player_entity.get_component(HealthComponent)
    initial_max_hp = health.max_hp
    equipment_system.equip_item(player_entity, steel_helmet)
    assert health.max_hp == initial_max_hp + 5


def test_equip_helmet_maintains_hp_percentage(equipment_system, player_entity, steel_helmet):
    """Equipping helmet maintains HP percentage."""
    health = player_entity.get_component(HealthComponent)
    # Damage player to 50%
    health.hp = health.max_hp // 2  # 15 HP out of 30
    initial_hp = health.hp

    equipment_system.equip_item(player_entity, steel_helmet)
    # Max HP should be 35 now, HP should be 18 (50%, rounded)
    expected_hp = round(35 * 0.5)
    assert health.hp == expected_hp


def test_equip_item_emits_event(equipment_system, event_bus, player_entity, iron_sword):
    """Equipping item emits EquipEvent."""
    events_received = []
    event_bus.subscribe("equip", lambda e: events_received.append(e))

    equipment_system.equip_item(player_entity, iron_sword)

    assert len(events_received) == 1
    event = events_received[0]
    assert isinstance(event, EquipEvent)
    assert event.entity_name == "Player"
    assert event.item_name == "Iron Sword"
    assert event.slot == "weapon"
    assert event.power_bonus == 3


def test_equip_replaces_previous_weapon(equipment_system, player_entity, iron_sword, steel_sword):
    """Equipping new weapon replaces old weapon."""
    equipment_system.equip_item(player_entity, iron_sword)
    previous = equipment_system.equip_item(player_entity, steel_sword)
    assert previous == iron_sword


def test_equip_replacing_weapon_unapplies_old_bonuses(
    equipment_system, player_entity, iron_sword, steel_sword
):
    """Equipping new weapon unapplies old weapon bonuses."""
    combat = player_entity.get_component(CombatComponent)
    initial_power = combat.power

    equipment_system.equip_item(player_entity, iron_sword)  # +3
    equipment_system.equip_item(player_entity, steel_sword)  # +5

    # Should have initial + 5 (not initial + 3 + 5)
    assert combat.power == initial_power + 5


def test_unequip_weapon_removes_power_bonus(equipment_system, player_entity, iron_sword):
    """Unequipping weapon removes power bonus."""
    combat = player_entity.get_component(CombatComponent)
    initial_power = combat.power

    equipment_system.equip_item(player_entity, iron_sword)
    equipment_system.unequip_item(player_entity, EquipmentSlot.WEAPON)

    assert combat.power == initial_power


def test_unequip_armor_removes_defense_bonus(equipment_system, player_entity, leather_armor):
    """Unequipping armor removes defense bonus."""
    combat = player_entity.get_component(CombatComponent)
    initial_defense = combat.defense

    equipment_system.equip_item(player_entity, leather_armor)
    equipment_system.unequip_item(player_entity, EquipmentSlot.ARMOR)

    assert combat.defense == initial_defense


def test_unequip_helmet_removes_max_hp_bonus(equipment_system, player_entity, steel_helmet):
    """Unequipping helmet removes max HP bonus."""
    health = player_entity.get_component(HealthComponent)
    initial_max_hp = health.max_hp

    equipment_system.equip_item(player_entity, steel_helmet)
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)

    assert health.max_hp == initial_max_hp


def test_unequip_helmet_clamps_hp_to_new_max(equipment_system, player_entity, steel_helmet):
    """Unequipping helmet clamps current HP to new max."""
    health = player_entity.get_component(HealthComponent)
    # Equip helmet (+5 max HP)
    equipment_system.equip_item(player_entity, steel_helmet)
    # Heal to full (35 HP)
    health.hp = health.max_hp

    # Unequip helmet (max HP back to 30)
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)

    # HP should be clamped to 30
    assert health.hp == 30


def test_unequip_item_emits_event(equipment_system, event_bus, player_entity, iron_sword):
    """Unequipping item emits UnequipEvent."""
    events_received = []
    event_bus.subscribe("unequip", lambda e: events_received.append(e))

    equipment_system.equip_item(player_entity, iron_sword)
    equipment_system.unequip_item(player_entity, EquipmentSlot.WEAPON)

    assert len(events_received) == 1
    event = events_received[0]
    assert isinstance(event, UnequipEvent)
    assert event.entity_name == "Player"
    assert event.item_name == "Iron Sword"
    assert event.slot == "weapon"


def test_unequip_empty_slot_returns_none(equipment_system, player_entity):
    """Unequipping empty slot returns None."""
    result = equipment_system.unequip_item(player_entity, EquipmentSlot.WEAPON)
    assert result is None


def test_unequip_empty_slot_does_not_emit_event(equipment_system, event_bus, player_entity):
    """Unequipping empty slot does not emit event."""
    events_received = []
    event_bus.subscribe("unequip", lambda e: events_received.append(e))

    equipment_system.unequip_item(player_entity, EquipmentSlot.WEAPON)

    assert len(events_received) == 0


def test_equip_item_without_equipment_component_raises_error(equipment_system, iron_sword):
    """Equipping item on entity without EquipmentComponent raises ValueError."""
    entity_no_equipment = ComponentEntity(Position(0, 0), "@", "Test", True)

    with pytest.raises(ValueError, match="has no EquipmentComponent"):
        equipment_system.equip_item(entity_no_equipment, iron_sword)


def test_equip_item_without_equipment_stats_raises_error(equipment_system, player_entity):
    """Equipping item without EquipmentStats raises ValueError."""
    invalid_item = ComponentEntity(Position(0, 0), "X", "Invalid", False)

    with pytest.raises(ValueError, match="has no EquipmentStats component"):
        equipment_system.equip_item(player_entity, invalid_item)


def test_unequip_item_without_equipment_component_raises_error(equipment_system):
    """Unequipping from entity without EquipmentComponent raises ValueError."""
    entity_no_equipment = ComponentEntity(Position(0, 0), "@", "Test", True)

    with pytest.raises(ValueError, match="has no EquipmentComponent"):
        equipment_system.unequip_item(entity_no_equipment, EquipmentSlot.WEAPON)


def test_get_effective_power_no_equipment(equipment_system, player_entity):
    """get_effective_power returns base power with no equipment."""
    combat = player_entity.get_component(CombatComponent)
    effective_power = equipment_system.get_effective_power(player_entity)
    assert effective_power == combat.power


def test_get_effective_power_with_equipment(equipment_system, player_entity, iron_sword):
    """get_effective_power includes equipment bonuses."""
    combat = player_entity.get_component(CombatComponent)
    equipment_system.equip_item(player_entity, iron_sword)
    effective_power = equipment_system.get_effective_power(player_entity)
    # Note: This returns base power (already modified by equip_item)
    # In actual combat, we might want to use this differently
    assert effective_power == combat.power


def test_get_effective_defense_no_equipment(equipment_system, player_entity):
    """get_effective_defense returns base defense with no equipment."""
    combat = player_entity.get_component(CombatComponent)
    effective_defense = equipment_system.get_effective_defense(player_entity)
    assert effective_defense == combat.defense


def test_get_effective_defense_with_equipment(equipment_system, player_entity, leather_armor):
    """get_effective_defense includes equipment bonuses."""
    combat = player_entity.get_component(CombatComponent)
    equipment_system.equip_item(player_entity, leather_armor)
    effective_defense = equipment_system.get_effective_defense(player_entity)
    assert effective_defense == combat.defense


def test_equip_multiple_items_different_slots(
    equipment_system, player_entity, iron_sword, leather_armor, steel_helmet
):
    """Equipping items in different slots all apply bonuses."""
    combat = player_entity.get_component(CombatComponent)
    health = player_entity.get_component(HealthComponent)

    initial_power = combat.power
    initial_defense = combat.defense
    initial_max_hp = health.max_hp

    equipment_system.equip_item(player_entity, iron_sword)  # +3 power
    equipment_system.equip_item(player_entity, leather_armor)  # +2 defense
    equipment_system.equip_item(player_entity, steel_helmet)  # +1 defense, +5 max HP

    assert combat.power == initial_power + 3
    assert combat.defense == initial_defense + 3  # 2 + 1
    assert health.max_hp == initial_max_hp + 5


def test_unequip_maintains_hp_percentage_after_damage(equipment_system, player_entity, steel_helmet):
    """Unequipping after taking damage maintains HP percentage (prevents free healing exploit)."""
    health = player_entity.get_component(HealthComponent)

    # Equip helmet at full HP: 30 HP -> 35 HP (max), HP becomes 35 (100% of 35)
    equipment_system.equip_item(player_entity, steel_helmet)
    assert health.max_hp == 35
    assert health.hp == 35  # Full HP at new max

    # Take damage to ~69% HP: 35 * 0.69 = 24.15 -> 24 HP
    health.hp = 24
    assert health.hp == 24
    assert health.max_hp == 35

    # Unequip helmet: should maintain ~69% HP
    # 30 * (24/35) = 30 * 0.6857 = 20.57 -> rounds to 21 HP (not 24 HP!)
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)
    assert health.max_hp == 30
    assert health.hp == round(30 * (24 / 35))  # Maintains percentage: 21 HP


def test_equipment_toggling_does_not_heal(equipment_system, player_entity, steel_helmet):
    """Repeatedly equipping/unequipping does not provide free healing."""
    health = player_entity.get_component(HealthComponent)

    # Start at 50% HP
    health.hp = 15  # 15/30 = 50%

    # Equip helmet: 30 -> 35 max HP, HP becomes 18 (50% of 35, rounded)
    equipment_system.equip_item(player_entity, steel_helmet)
    assert health.max_hp == 35
    assert health.hp == round(35 * 0.5)  # 18 HP

    # Unequip helmet: 35 -> 30 max HP, HP becomes 15 (rounds to 15)
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)
    assert health.max_hp == 30
    assert health.hp == round(30 * (18 / 35))  # 15 HP (maintains percentage)

    # Re-equip helmet: 30 -> 35 max HP, HP becomes 18 (15/30 = 50% -> 18 HP)
    equipment_system.equip_item(player_entity, steel_helmet)
    assert health.max_hp == 35
    hp_after_reequip = health.hp
    expected_hp = round(35 * (15 / 30))  # 18 HP
    assert hp_after_reequip == expected_hp

    # Unequip again: HP should decrease proportionally, not stay at higher value
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)
    assert health.max_hp == 30
    assert health.hp == round(30 * (hp_after_reequip / 35))  # Maintains percentage


def test_unequip_very_low_hp_maintains_percentage(equipment_system, player_entity, steel_helmet):
    """Unequipping at very low HP maintains percentage correctly."""
    health = player_entity.get_component(HealthComponent)

    # Equip helmet: 30 -> 35 max HP
    equipment_system.equip_item(player_entity, steel_helmet)
    assert health.max_hp == 35

    # Take damage to ~8.6% HP: 3/35
    health.hp = 3
    hp_percentage = 3 / 35  # ~8.57%

    # Unequip: should maintain percentage with rounding
    # 30 * 0.0857 = 2.57 -> rounds to 3 HP
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)
    assert health.max_hp == 30
    expected_hp = round(30 * hp_percentage)  # 3 HP (rounded)
    assert health.hp == expected_hp


def test_unequip_extremely_low_hp_does_not_kill_player(equipment_system, player_entity):
    """Unequipping large HP bonus at 1 HP does not kill player (bug fix test)."""
    health = player_entity.get_component(HealthComponent)

    # Create item with large HP bonus
    large_hp_item = ComponentEntity(Position(0, 0), "^", "Legendary Helmet", False)
    large_hp_item.add_component(
        EquipmentStats(slot=EquipmentSlot.HELMET, max_hp_bonus=100)
    )

    # Equip: 30 -> 130 max HP, HP becomes 130
    equipment_system.equip_item(player_entity, large_hp_item)
    assert health.max_hp == 130
    assert health.hp == 130

    # Take massive damage to 1 HP (0.77% of max)
    health.hp = 1
    hp_percentage = 1 / 130  # ~0.77%

    # Unequip: 130 -> 30 max HP
    # Without fix: int(30 * 0.0077) = int(0.23) = 0 HP (DEAD!)
    # With fix: round(30 * 0.0077) = round(0.23) = 0, but clamped to 1 HP
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)
    assert health.max_hp == 30
    assert health.hp == 1  # Player survives!
    assert health.is_alive


def test_equip_extremely_low_hp_does_not_kill_player(equipment_system, player_entity):
    """Equipping large HP bonus at 1 HP does not kill player."""
    health = player_entity.get_component(HealthComponent)

    # Damage to 1 HP
    health.hp = 1
    hp_percentage = 1 / 30  # ~3.33%

    # Create item with large HP bonus
    large_hp_item = ComponentEntity(Position(0, 0), "^", "Legendary Helmet", False)
    large_hp_item.add_component(
        EquipmentStats(slot=EquipmentSlot.HELMET, max_hp_bonus=100)
    )

    # Equip: 30 -> 130 max HP
    # round(130 * 0.0333) = round(4.33) = 4 HP
    equipment_system.equip_item(player_entity, large_hp_item)
    assert health.max_hp == 130
    expected_hp = round(130 * hp_percentage)  # 4 HP
    assert health.hp == expected_hp
    assert health.is_alive


def test_rounding_favors_player_survival(equipment_system, player_entity, steel_helmet):
    """Rounding uses round() not int() truncation."""
    health = player_entity.get_component(HealthComponent)

    # Equip helmet: 30 -> 35 max HP
    equipment_system.equip_item(player_entity, steel_helmet)
    assert health.max_hp == 35

    # Set HP to value where rounding matters: 2/35 = 5.71%
    health.hp = 2
    hp_percentage = 2 / 35

    # Unequip: 35 -> 30 max HP
    # With int(): int(30 * 0.0571) = int(1.71) = 1 HP
    # With round(): round(30 * 0.0571) = round(1.71) = 2 HP
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)
    assert health.max_hp == 30
    expected_hp = round(30 * hp_percentage)  # 2 HP
    assert health.hp == expected_hp


def test_dead_entity_stays_dead(equipment_system, player_entity, steel_helmet):
    """Entity that dies stays at 0 HP when equipment changes."""
    health = player_entity.get_component(HealthComponent)

    # Equip helmet
    equipment_system.equip_item(player_entity, steel_helmet)
    assert health.max_hp == 35

    # Entity dies (0 HP)
    health.hp = 0
    assert not health.is_alive

    # Unequip: should stay at 0 HP
    equipment_system.unequip_item(player_entity, EquipmentSlot.HELMET)
    assert health.max_hp == 30
    assert health.hp == 0
    assert not health.is_alive


def test_swap_equipment_emits_both_events(equipment_system, event_bus, player_entity, iron_sword, steel_sword):
    """Swapping equipment emits both UnequipEvent and EquipEvent."""
    equip_events = []
    unequip_events = []
    event_bus.subscribe("equip", lambda e: equip_events.append(e))
    event_bus.subscribe("unequip", lambda e: unequip_events.append(e))

    # Equip iron sword (first equip - no unequip event)
    equipment_system.equip_item(player_entity, iron_sword)
    assert len(equip_events) == 1
    assert len(unequip_events) == 0

    # Swap to steel sword (should emit both events)
    equipment_system.equip_item(player_entity, steel_sword)
    assert len(equip_events) == 2
    assert len(unequip_events) == 1


def test_swap_equipment_unequip_event_has_correct_details(
    equipment_system, event_bus, player_entity, iron_sword, steel_sword
):
    """Swapping equipment emits UnequipEvent with correct old item details."""
    unequip_events = []
    event_bus.subscribe("unequip", lambda e: unequip_events.append(e))

    # Equip iron sword then swap to steel sword
    equipment_system.equip_item(player_entity, iron_sword)
    equipment_system.equip_item(player_entity, steel_sword)

    # Check the unequip event for iron sword
    assert len(unequip_events) == 1
    event = unequip_events[0]
    assert isinstance(event, UnequipEvent)
    assert event.entity_name == "Player"
    assert event.item_name == "Iron Sword"  # Old item
    assert event.slot == "weapon"


def test_swap_equipment_events_in_correct_order(
    equipment_system, event_bus, player_entity, iron_sword, steel_sword
):
    """Swapping equipment emits UnequipEvent before EquipEvent."""
    all_events = []
    event_bus.subscribe("equip", lambda e: all_events.append(("equip", e)))
    event_bus.subscribe("unequip", lambda e: all_events.append(("unequip", e)))

    # Equip iron sword then swap to steel sword
    equipment_system.equip_item(player_entity, iron_sword)
    all_events.clear()  # Clear the first equip event

    equipment_system.equip_item(player_entity, steel_sword)

    # Should have unequip event first, then equip event
    assert len(all_events) == 2
    assert all_events[0][0] == "unequip"
    assert all_events[0][1].item_name == "Iron Sword"
    assert all_events[1][0] == "equip"
    assert all_events[1][1].item_name == "Steel Sword"


def test_equip_to_empty_slot_only_emits_equip_event(
    equipment_system, event_bus, player_entity, iron_sword
):
    """Equipping to empty slot only emits EquipEvent, not UnequipEvent."""
    equip_events = []
    unequip_events = []
    event_bus.subscribe("equip", lambda e: equip_events.append(e))
    event_bus.subscribe("unequip", lambda e: unequip_events.append(e))

    # Equip to empty slot
    equipment_system.equip_item(player_entity, iron_sword)

    # Should only have equip event
    assert len(equip_events) == 1
    assert len(unequip_events) == 0
