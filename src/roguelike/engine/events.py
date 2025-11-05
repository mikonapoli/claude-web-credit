"""Event system for decoupled game event handling."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Event:
    """Base event class."""

    type: str
    data: dict[str, Any]


@dataclass
class CombatEvent(Event):
    """Combat event with structured data."""

    def __init__(
        self,
        attacker_name: str,
        defender_name: str,
        damage: int,
        defender_died: bool,
    ):
        """Initialize combat event."""
        self.type = "combat"
        self.attacker_name = attacker_name
        self.defender_name = defender_name
        self.damage = damage
        self.defender_died = defender_died
        self.data = {
            "attacker_name": attacker_name,
            "defender_name": defender_name,
            "damage": damage,
            "defender_died": defender_died,
        }


@dataclass
class DeathEvent(Event):
    """Entity death event."""

    def __init__(self, entity_name: str, xp_value: int, killed_by_player: bool):
        """Initialize death event."""
        self.type = "death"
        self.entity_name = entity_name
        self.xp_value = xp_value
        self.killed_by_player = killed_by_player
        self.data = {
            "entity_name": entity_name,
            "xp_value": xp_value,
            "killed_by_player": killed_by_player,
        }


@dataclass
class LevelUpEvent(Event):
    """Level up event."""

    def __init__(self, entity_name: str, new_level: int, stat_increases: dict[str, int]):
        """Initialize level up event."""
        self.type = "level_up"
        self.entity_name = entity_name
        self.new_level = new_level
        self.stat_increases = stat_increases
        self.data = {
            "entity_name": entity_name,
            "new_level": new_level,
            "stat_increases": stat_increases,
        }


@dataclass
class XPGainEvent(Event):
    """XP gain event."""

    def __init__(self, entity_name: str, xp_gained: int):
        """Initialize XP gain event."""
        self.type = "xp_gain"
        self.entity_name = entity_name
        self.xp_gained = xp_gained
        self.data = {
            "entity_name": entity_name,
            "xp_gained": xp_gained,
        }


@dataclass
class SpellCastEvent(Event):
    """Spell cast event."""

    def __init__(
        self,
        caster_name: str,
        spell_name: str,
        target_name: str,
        mana_cost: int,
        effect_message: str,
    ):
        """Initialize spell cast event."""
        self.type = "spell_cast"
        self.caster_name = caster_name
        self.spell_name = spell_name
        self.target_name = target_name
        self.mana_cost = mana_cost
        self.effect_message = effect_message
        self.data = {
            "caster_name": caster_name,
            "spell_name": spell_name,
            "target_name": target_name,
            "mana_cost": mana_cost,
            "effect_message": effect_message,
        }


@dataclass
class LevelTransitionEvent(Event):
    """Level transition event."""

    def __init__(self, new_level: int, level_name: str):
        """Initialize level transition event.

        Args:
            new_level: The level number being transitioned to
            level_name: The name of the new level
        """
        self.type = "level_transition"
        self.new_level = new_level
        self.level_name = level_name
        self.data = {
            "new_level": new_level,
            "level_name": level_name,
        }


@dataclass
class ItemPickupEvent(Event):
    """Item pickup event."""

    def __init__(self, entity_name: str, item_name: str):
        """Initialize item pickup event."""
        self.type = "item_pickup"
        self.entity_name = entity_name
        self.item_name = item_name
        self.data = {
            "entity_name": entity_name,
            "item_name": item_name,
        }


@dataclass
class ItemUseEvent(Event):
    """Item use event."""

    def __init__(self, entity_name: str, item_name: str, item_type: str):
        """Initialize item use event."""
        self.type = "item_use"
        self.entity_name = entity_name
        self.item_name = item_name
        self.item_type = item_type
        self.data = {
            "entity_name": entity_name,
            "item_name": item_name,
            "item_type": item_type,
        }


@dataclass
class ManaChangedEvent(Event):
    """Mana changed event."""

    def __init__(self, entity_name: str, old_mp: int, new_mp: int, max_mp: int):
        """Initialize mana changed event."""
        self.type = "mana_changed"
        self.entity_name = entity_name
        self.old_mp = old_mp
        self.new_mp = new_mp
        self.max_mp = max_mp
        self.data = {
            "entity_name": entity_name,
            "old_mp": old_mp,
            "new_mp": new_mp,
            "max_mp": max_mp,
        }


@dataclass
class HealingEvent(Event):
    """Healing event."""

    def __init__(self, entity_name: str, amount_healed: int):
        """Initialize healing event."""
        self.type = "healing"
        self.entity_name = entity_name
        self.amount_healed = amount_healed
        self.data = {
            "entity_name": entity_name,
            "amount_healed": amount_healed,
        }


@dataclass
class CraftingAttemptEvent(Event):
    """Event emitted when crafting is attempted."""

    def __init__(
        self,
        crafter_name: str,
        ingredient_names: list[str],
        success: bool,
        result_name: str | None = None,
    ):
        """Initialize crafting attempt event.

        Args:
            crafter_name: Name of entity performing crafting
            ingredient_names: Names of ingredients used
            success: Whether crafting succeeded
            result_name: Name of resulting item (if successful)
        """
        self.type = "crafting_attempt"
        self.crafter_name = crafter_name
        self.ingredient_names = ingredient_names
        self.success = success
        self.result_name = result_name
        self.data = {
            "crafter_name": crafter_name,
            "ingredient_names": ingredient_names,
            "success": success,
            "result_name": result_name,
        }


@dataclass
class RecipeDiscoveredEvent(Event):
    """Event emitted when a new recipe is discovered."""

    def __init__(self, recipe_id: str, recipe_name: str, discoverer_name: str):
        """Initialize recipe discovered event.

        Args:
            recipe_id: ID of discovered recipe
            recipe_name: Name of discovered recipe
            discoverer_name: Name of entity who discovered it
        """
        self.type = "recipe_discovered"
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name
        self.discoverer_name = discoverer_name
        self.data = {
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "discoverer_name": discoverer_name,
        }


@dataclass
class StatusEffectAppliedEvent(Event):
    """Event emitted when a status effect is applied to an entity."""

    def __init__(
        self, entity_name: str, effect_type: str, duration: int, power: int = 0
    ):
        """Initialize status effect applied event.

        Args:
            entity_name: Name of entity receiving the effect
            effect_type: Type of status effect (poison, confusion, etc.)
            duration: Number of turns the effect will last
            power: Effect strength/magnitude
        """
        self.type = "status_effect_applied"
        self.entity_name = entity_name
        self.effect_type = effect_type
        self.duration = duration
        self.power = power
        self.data = {
            "entity_name": entity_name,
            "effect_type": effect_type,
            "duration": duration,
            "power": power,
        }


@dataclass
class StatusEffectExpiredEvent(Event):
    """Event emitted when a status effect expires."""

    def __init__(self, entity_name: str, effect_type: str):
        """Initialize status effect expired event.

        Args:
            entity_name: Name of entity losing the effect
            effect_type: Type of status effect that expired
        """
        self.type = "status_effect_expired"
        self.entity_name = entity_name
        self.effect_type = effect_type
        self.data = {
            "entity_name": entity_name,
            "effect_type": effect_type,
class EquipEvent(Event):
    """Event emitted when an item is equipped."""

    def __init__(
        self,
        entity_name: str,
        item_name: str,
        slot: str,
        power_bonus: int = 0,
        defense_bonus: int = 0,
        max_hp_bonus: int = 0,
    ):
        """Initialize equip event.

        Args:
            entity_name: Name of entity equipping item
            item_name: Name of item being equipped
            slot: Equipment slot (weapon, armor, etc.)
            power_bonus: Power bonus from item
            defense_bonus: Defense bonus from item
            max_hp_bonus: Max HP bonus from item
        """
        self.type = "equip"
        self.entity_name = entity_name
        self.item_name = item_name
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.data = {
            "entity_name": entity_name,
            "item_name": item_name,
            "slot": slot,
            "power_bonus": power_bonus,
            "defense_bonus": defense_bonus,
            "max_hp_bonus": max_hp_bonus,
        }


@dataclass
class StatusEffectTickEvent(Event):
    """Event emitted when a status effect processes each turn."""
class UnequipEvent(Event):
    """Event emitted when an item is unequipped."""

    def __init__(
        self,
        entity_name: str,
        effect_type: str,
        power: int,
        remaining_duration: int,
        item_name: str,
        slot: str,
    ):
        """Initialize status effect tick event.

        Args:
            entity_name: Name of entity with the effect
            effect_type: Type of status effect
            power: Effect strength/magnitude
            remaining_duration: Turns remaining after this tick
            item_name: Name of item being unequipped
            slot: Equipment slot (weapon, armor, etc.)
        """
        self.type = "status_effect_tick"
        self.entity_name = entity_name
        self.effect_type = effect_type
        self.power = power
        self.remaining_duration = remaining_duration
        self.item_name = item_name
        self.slot = slot
        self.data = {
            "entity_name": entity_name,
            "effect_type": effect_type,
            "power": power,
            "remaining_duration": remaining_duration,
            "item_name": item_name,
            "slot": slot,
        }


class EventBus:
    """Simple event bus for pub/sub pattern."""

    def __init__(self):
        """Initialize event bus."""
        self.subscribers: dict[str, list[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Callback function to call when event is emitted
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def emit(self, event: Event) -> None:
        """Emit an event to all subscribers.

        Args:
            event: Event to emit
        """
        for callback in self.subscribers.get(event.type, []):
            callback(event)

    def clear(self) -> None:
        """Clear all subscribers."""
        self.subscribers.clear()
