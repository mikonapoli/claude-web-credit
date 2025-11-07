"""Item system for handling item effects."""

from typing import List, Optional

from roguelike.engine.events import EventBus, HealingEvent, ItemUseEvent
from roguelike.components.entity import ComponentEntity
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

    def use_item(self, item: Item, user: ComponentEntity, inventory: Inventory, target: Optional[ComponentEntity] = None) -> bool:
        """Use an item and apply its effects.

        Args:
            item: Item to use
            user: ComponentEntity using the item
            inventory: User's inventory
            target: Optional target actor for targeted items

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
        success = self._apply_item_effect(item, user, target)

        # Remove item from inventory if used successfully
        if success:
            inventory.remove(item)

        return success

    def _apply_item_effect(self, item: Item, user: ComponentEntity, target: Optional[ComponentEntity] = None) -> bool:
        """Apply the effect of an item.

        Args:
            item: Item being used
            user: ComponentEntity using the item
            target: Optional target actor for targeted items

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
            return self._apply_fireball(item, user, target)
        elif item_type == ItemType.SCROLL_LIGHTNING:
            return self._apply_lightning(item, user, target)
        elif item_type == ItemType.SCROLL_CONFUSION:
            return self._apply_confusion(item, user, target)

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

    def _apply_healing(self, item: Item, user: ComponentEntity) -> bool:
        """Apply healing effect.

        Args:
            item: Healing item
            user: ComponentEntity to heal

        Returns:
            True if healing was applied
        """
        if user.hp >= user.max_hp:
            return False

        amount_healed = user.heal(item.value)
        self.event_bus.emit(HealingEvent(entity_name=user.name, amount_healed=amount_healed))
        return True

    def _apply_strength_buff(self, item: Item, user: ComponentEntity) -> bool:
        """Apply strength buff.

        Note: Currently applies permanent power boost.
        A temporary buff system could be added in the future.

        Args:
            item: Strength potion
            user: ComponentEntity to buff

        Returns:
            True if buff was applied
        """
        # Apply permanent power boost
        user.power += item.value
        return True

    def _apply_defense_buff(self, item: Item, user: ComponentEntity) -> bool:
        """Apply defense buff.

        Note: Currently applies permanent defense boost.
        A temporary buff system could be added in the future.

        Args:
            item: Defense potion
            user: ComponentEntity to buff

        Returns:
            True if buff was applied
        """
        # Apply permanent defense boost
        user.defense += item.value
        return True

    def _apply_speed_buff(self, item: Item, user: ComponentEntity) -> bool:
        """Apply speed buff.

        Note: This is a stub - speed/turn system not yet implemented.
        Currently consumes the item but has no effect.

        Args:
            item: Speed potion
            user: ComponentEntity to buff

        Returns:
            True (item consumed with no effect)
        """
        # Speed/turn system not yet implemented
        return True

    def _apply_invisibility(self, item: Item, user: ComponentEntity) -> bool:
        """Apply invisibility effect.

        Args:
            item: Invisibility potion
            user: ComponentEntity to make invisible

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            return self.status_effects_system.apply_effect(
                user, "invisibility", duration=item.value, power=0
            )
        return False

    def _apply_gigantism(self, item: Item, user: ComponentEntity) -> bool:
        """Apply gigantism effect.

        Note: Currently applies permanent power boost.
        A temporary buff system could be added in the future.

        Args:
            item: Gigantism potion
            user: ComponentEntity to grow

        Returns:
            True if effect was applied
        """
        # Apply permanent power boost (representing growth)
        user.power += item.value
        return True

    def _apply_shrinking(self, item: Item, user: ComponentEntity) -> bool:
        """Apply shrinking effect.

        Note: Currently applies permanent defense boost.
        A temporary buff system could be added in the future.

        Args:
            item: Shrinking potion
            user: ComponentEntity to shrink

        Returns:
            True if effect was applied
        """
        # Apply permanent defense boost (representing evasiveness from being small)
        user.defense += item.value
        return True

    def _apply_fireball(self, item: Item, user: ComponentEntity, target: Optional[ComponentEntity] = None) -> bool:
        """Apply fireball effect.

        Note: This is a stub - AoE damage system not yet implemented.
        Currently validates target but does no damage.

        Args:
            item: Fireball scroll
            user: ComponentEntity casting fireball
            target: Target actor (required)

        Returns:
            True if target is valid (but no damage is dealt)
        """
        # AoE damage system not yet implemented
        if not target or not target.is_alive:
            return False
        return True

    def _apply_lightning(self, item: Item, user: ComponentEntity, target: Optional[ComponentEntity] = None) -> bool:
        """Apply lightning effect.

        Note: This is a stub - single-target damage not yet implemented.
        Currently validates target but does no damage.

        Args:
            item: Lightning scroll
            user: ComponentEntity casting lightning
            target: Target actor (required)

        Returns:
            True if target is valid (but no damage is dealt)
        """
        # Single-target damage not yet implemented
        if not target or not target.is_alive:
            return False
        return True

    def _apply_confusion(self, item: Item, user: ComponentEntity, target: Optional[ComponentEntity] = None) -> bool:
        """Apply confusion effect.

        Args:
            item: Confusion scroll
            user: ComponentEntity casting confusion
            target: Target actor (required for targeted use)

        Returns:
            True if effect was applied
        """
        if not target or not target.is_alive:
            return False

        if self.status_effects_system:
            return self.status_effects_system.apply_effect(
                target, "confusion", duration=item.value, power=0
            )
        return False

    def _apply_teleport(self, item: Item, user: ComponentEntity) -> bool:
        """Apply teleport effect.

        Note: This is a stub - random teleportation not yet implemented.
        Currently consumes the item but has no effect.

        Args:
            item: Teleport scroll
            user: ComponentEntity to teleport

        Returns:
            True (item consumed with no effect)
        """
        # Random teleportation not yet implemented
        return True

    def _apply_magic_mapping(self, item: Item, user: ComponentEntity) -> bool:
        """Apply magic mapping effect.

        Note: This is a stub - map reveal not yet implemented.
        Currently consumes the item but has no effect.

        Args:
            item: Magic mapping scroll
            user: ComponentEntity revealing map

        Returns:
            True (item consumed with no effect)
        """
        # Map reveal not yet implemented
        return True

    def _apply_coffee(self, item: Item, user: ComponentEntity) -> bool:
        """Apply coffee effect.

        Note: This is a stub - speed boost not yet implemented.
        Currently consumes the item but has no effect.

        Args:
            item: Coffee
            user: ComponentEntity drinking coffee

        Returns:
            True (item consumed with no effect)
        """
        # Speed boost not yet implemented
        return True

    def _apply_lucky_coin(self, item: Item, user: ComponentEntity) -> bool:
        """Apply lucky coin effect.

        Note: This is a stub - XP boost not yet implemented.
        Currently consumes the item but has no effect.

        Args:
            item: Lucky coin
            user: ComponentEntity using coin

        Returns:
            True (item consumed with no effect)
        """
        # XP boost not yet implemented
        return True

    def _apply_banana_peel(self, item: Item, user: ComponentEntity) -> bool:
        """Apply banana peel effect.

        Note: This is a stub - throwable trap not yet implemented.
        Currently consumes the item but has no effect.

        Args:
            item: Banana peel
            user: ComponentEntity throwing banana peel

        Returns:
            True (item consumed with no effect)
        """
        # Throwable trap not yet implemented
        return True

    def _apply_rubber_chicken(self, item: Item, user: ComponentEntity) -> bool:
        """Apply rubber chicken effect.

        Note: This is a stub - weak attack not yet implemented.
        Currently consumes the item but has no effect.

        Args:
            item: Rubber chicken
            user: ComponentEntity using rubber chicken

        Returns:
            True (item consumed with no effect)
        """
        # Weak attack not yet implemented
        return True

    def _apply_cursed_ring(self, item: Item, user: ComponentEntity) -> bool:
        """Apply cursed ring effect.

        Args:
            item: Cursed ring
            user: ComponentEntity using ring

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
