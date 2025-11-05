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
