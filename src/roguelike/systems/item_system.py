"""Item system for handling item effects."""

from typing import List, Optional

from roguelike.engine.events import EventBus, HealingEvent, ItemUseEvent
from roguelike.entities.actor import Actor
from roguelike.entities.item import Item, ItemType
from roguelike.systems.inventory import Inventory
from roguelike.systems.status_effects import StatusEffectsSystem


class ItemSystem:
    """Manages item usage and effects."""

    def __init__(
        self, event_bus: EventBus, status_effects_system: Optional[StatusEffectsSystem] = None
    ):
        """Initialize item system.

        Args:
            event_bus: Event bus for publishing item events
            status_effects_system: Status effects system for applying effects
        """
        self.event_bus = event_bus
        self.status_effects_system = status_effects_system

    def use_item(self, item: Item, user: Actor, inventory: Inventory) -> bool:
        """Use an item and apply its effects.

        Args:
            item: Item to use
            user: Actor using the item
            inventory: User's inventory

        Returns:
            True if item was used successfully
        """
        # Emit item use event
        self.event_bus.emit(
            ItemUseEvent(
                entity_name=user.name,
                item_name=item.name,
                item_type=item.item_type.value,
            )
        )

        # Apply item effect based on type
        success = self._apply_item_effect(item, user)

        # Remove item from inventory if used successfully
        if success:
            inventory.remove(item)

        return success

    def _apply_item_effect(self, item: Item, user: Actor) -> bool:
        """Apply the effect of an item.

        Args:
            item: Item being used
            user: Actor using the item

        Returns:
            True if effect was applied successfully
        """
        item_type = item.item_type

        # Healing items
        if item_type in (
            ItemType.HEALING_POTION,
            ItemType.GREATER_HEALING_POTION,
            ItemType.CHEESE_WHEEL,
        ):
            return self._apply_healing(item, user)

        # Buff potions
        elif item_type == ItemType.STRENGTH_POTION:
            return self._apply_strength_buff(item, user)
        elif item_type == ItemType.DEFENSE_POTION:
            return self._apply_defense_buff(item, user)
        elif item_type == ItemType.SPEED_POTION:
            return self._apply_speed_buff(item, user)
        elif item_type == ItemType.INVISIBILITY_POTION:
            return self._apply_invisibility(item, user)
        elif item_type == ItemType.GIGANTISM_POTION:
            return self._apply_gigantism(item, user)
        elif item_type == ItemType.SHRINKING_POTION:
            return self._apply_shrinking(item, user)

        # Combat scrolls
        elif item_type == ItemType.SCROLL_FIREBALL:
            return self._apply_fireball(item, user)
        elif item_type == ItemType.SCROLL_LIGHTNING:
            return self._apply_lightning(item, user)
        elif item_type == ItemType.SCROLL_CONFUSION:
            return self._apply_confusion(item, user)

        # Utility scrolls
        elif item_type == ItemType.SCROLL_TELEPORT:
            return self._apply_teleport(item, user)
        elif item_type == ItemType.SCROLL_MAGIC_MAPPING:
            return self._apply_magic_mapping(item, user)

        # Quirky items
        elif item_type == ItemType.COFFEE:
            return self._apply_coffee(item, user)
        elif item_type == ItemType.LUCKY_COIN:
            return self._apply_lucky_coin(item, user)
        elif item_type == ItemType.BANANA_PEEL:
            return self._apply_banana_peel(item, user)
        elif item_type == ItemType.RUBBER_CHICKEN:
            return self._apply_rubber_chicken(item, user)
        elif item_type == ItemType.CURSED_RING:
            return self._apply_cursed_ring(item, user)

        return False

    def _apply_healing(self, item: Item, user: Actor) -> bool:
        """Apply healing effect.

        Args:
            item: Healing item
            user: Actor to heal

        Returns:
            True if healing was applied
        """
        if user.hp >= user.max_hp:
            return False

        amount_healed = user.heal(item.value)
        self.event_bus.emit(HealingEvent(entity_name=user.name, amount_healed=amount_healed))
        return True

    def _apply_strength_buff(self, item: Item, user: Actor) -> bool:
        """Apply strength buff.

        Args:
            item: Strength potion
            user: Actor to buff

        Returns:
            True if buff was applied
        """
        # TODO: Implement temporary buff system
        # For now, just apply permanent boost
        user.power += item.value
        return True

    def _apply_defense_buff(self, item: Item, user: Actor) -> bool:
        """Apply defense buff.

        Args:
            item: Defense potion
            user: Actor to buff

        Returns:
            True if buff was applied
        """
        # TODO: Implement temporary buff system
        user.defense += item.value
        return True

    def _apply_speed_buff(self, item: Item, user: Actor) -> bool:
        """Apply speed buff.

        Args:
            item: Speed potion
            user: Actor to buff

        Returns:
            True if buff was applied
        """
        # TODO: Implement speed/turn system
        return True

    def _apply_invisibility(self, item: Item, user: Actor) -> bool:
        """Apply invisibility effect.

        Args:
            item: Invisibility potion
            user: Actor to make invisible

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            return self.status_effects_system.apply_effect(
                user, "invisibility", duration=item.value, power=0
            )
        return False

    def _apply_gigantism(self, item: Item, user: Actor) -> bool:
        """Apply gigantism effect.

        Args:
            item: Gigantism potion
            user: Actor to grow

        Returns:
            True if effect was applied
        """
        # TODO: Implement temporary buff system
        user.power += item.value
        return True

    def _apply_shrinking(self, item: Item, user: Actor) -> bool:
        """Apply shrinking effect.

        Args:
            item: Shrinking potion
            user: Actor to shrink

        Returns:
            True if effect was applied
        """
        # TODO: Implement temporary buff system
        user.defense += item.value
        return True

    def _apply_fireball(self, item: Item, user: Actor) -> bool:
        """Apply fireball effect.

        Args:
            item: Fireball scroll
            user: Actor casting fireball

        Returns:
            True if effect was applied
        """
        # TODO: Implement targeting and AoE damage
        return True

    def _apply_lightning(self, item: Item, user: Actor) -> bool:
        """Apply lightning effect.

        Args:
            item: Lightning scroll
            user: Actor casting lightning

        Returns:
            True if effect was applied
        """
        # TODO: Implement targeting and single-target damage
        return True

    def _apply_confusion(self, item: Item, user: Actor) -> bool:
        """Apply confusion effect.

        Args:
            item: Confusion scroll
            user: Actor casting confusion

        Returns:
            True if effect was applied
        """
        # TODO: Implement targeting system to confuse enemies instead of self
        # For now, applying to user for testing purposes
        if self.status_effects_system:
            return self.status_effects_system.apply_effect(
                user, "confusion", duration=item.value, power=0
            )
        return False

    def _apply_teleport(self, item: Item, user: Actor) -> bool:
        """Apply teleport effect.

        Args:
            item: Teleport scroll
            user: Actor to teleport

        Returns:
            True if effect was applied
        """
        # TODO: Implement random teleportation
        return True

    def _apply_magic_mapping(self, item: Item, user: Actor) -> bool:
        """Apply magic mapping effect.

        Args:
            item: Magic mapping scroll
            user: Actor revealing map

        Returns:
            True if effect was applied
        """
        # TODO: Implement map reveal
        return True

    def _apply_coffee(self, item: Item, user: Actor) -> bool:
        """Apply coffee effect.

        Args:
            item: Coffee
            user: Actor drinking coffee

        Returns:
            True if effect was applied
        """
        # TODO: Implement speed boost
        return True

    def _apply_lucky_coin(self, item: Item, user: Actor) -> bool:
        """Apply lucky coin effect.

        Args:
            item: Lucky coin
            user: Actor using coin

        Returns:
            True if effect was applied
        """
        # TODO: Implement XP boost
        return True

    def _apply_banana_peel(self, item: Item, user: Actor) -> bool:
        """Apply banana peel effect.

        Args:
            item: Banana peel
            user: Actor throwing banana peel

        Returns:
            True if effect was applied
        """
        # TODO: Implement throwable trap
        return True

    def _apply_rubber_chicken(self, item: Item, user: Actor) -> bool:
        """Apply rubber chicken effect.

        Args:
            item: Rubber chicken
            user: Actor using rubber chicken

        Returns:
            True if effect was applied
        """
        # TODO: Implement weak attack
        return True

    def _apply_cursed_ring(self, item: Item, user: Actor) -> bool:
        """Apply cursed ring effect.

        Args:
            item: Cursed ring
            user: Actor using ring

        Returns:
            True if effect was applied
        """
        import random

        # Random effect (50% chance good, 50% chance bad)
        effects = [
            ("good", "healing", lambda: user.heal(20)),
            ("good", "strength", lambda: setattr(user, "power", user.power + 2)),
            ("bad", "poison", lambda: self.status_effects_system.apply_effect(
                user, "poison", duration=5, power=2
            ) if self.status_effects_system else False),
            ("bad", "confusion", lambda: self.status_effects_system.apply_effect(
                user, "confusion", duration=3, power=0
            ) if self.status_effects_system else False),
            ("bad", "damage", lambda: user.take_damage(10)),
        ]

        effect_type, effect_name, effect_func = random.choice(effects)
        effect_func()
        return True
