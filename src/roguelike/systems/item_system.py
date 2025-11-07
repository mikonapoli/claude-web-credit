"""Item system for handling item effects."""

from typing import List, Optional, TYPE_CHECKING

from roguelike.engine.events import EventBus, HealingEvent, ItemUseEvent
from roguelike.components.entity import ComponentEntity
from roguelike.entities.item import Item, ItemType
from roguelike.systems.inventory import Inventory
from roguelike.systems.status_effects import StatusEffectsSystem

if TYPE_CHECKING:
    from roguelike.world.fov import FOVMap
    from roguelike.world.game_map import GameMap


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

    def use_item(
        self,
        item: Item,
        user: ComponentEntity,
        inventory: Inventory,
        target: Optional[ComponentEntity] = None,
        fov_map: Optional["FOVMap"] = None,
        game_map: Optional["GameMap"] = None,
        entities: Optional[List[ComponentEntity]] = None,
    ) -> bool:
        """Use an item and apply its effects.

        Args:
            item: Item to use
            user: ComponentEntity using the item
            inventory: User's inventory
            target: Optional target actor for targeted items
            fov_map: Optional FOV map for map-revealing effects
            game_map: Optional game map for teleportation effects
            entities: Optional list of entities for collision checking

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
        success = self._apply_item_effect(item, user, target, fov_map, game_map, entities)

        # Remove item from inventory if used successfully
        if success:
            inventory.remove(item)

        return success

    def _apply_item_effect(
        self,
        item: Item,
        user: ComponentEntity,
        target: Optional[ComponentEntity] = None,
        fov_map: Optional["FOVMap"] = None,
        game_map: Optional["GameMap"] = None,
        entities: Optional[List[ComponentEntity]] = None,
    ) -> bool:
        """Apply the effect of an item.

        Args:
            item: Item being used
            user: ComponentEntity using the item
            target: Optional target actor for targeted items
            fov_map: Optional FOV map for map-revealing effects
            game_map: Optional game map for teleportation effects
            entities: Optional list of entities for collision checking

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
            return self._apply_teleport(item, user, game_map, entities)
        elif item_type == ItemType.SCROLL_MAGIC_MAPPING:
            return self._apply_magic_mapping(item, user, fov_map)

        # Quirky items
        elif item_type == ItemType.COFFEE:
            return self._apply_coffee(item, user)
        elif item_type == ItemType.LUCKY_COIN:
            return self._apply_lucky_coin(item, user)
        elif item_type == ItemType.BANANA_PEEL:
            return self._apply_banana_peel(item, user, target)
        elif item_type == ItemType.RUBBER_CHICKEN:
            return self._apply_rubber_chicken(item, user, target)
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

        Temporarily increases power by growing in size.

        Args:
            item: Gigantism potion
            user: ComponentEntity to grow

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            # Apply temporary power boost via status effect
            # Duration is 10 turns, power value is the boost amount
            duration = 10
            return self.status_effects_system.apply_effect(
                user, "gigantism", duration=duration, power=item.value
            )
        return False

    def _apply_shrinking(self, item: Item, user: ComponentEntity) -> bool:
        """Apply shrinking effect.

        Temporarily increases defense by becoming smaller and harder to hit.

        Args:
            item: Shrinking potion
            user: ComponentEntity to shrink

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            # Apply temporary defense boost via status effect
            # Duration is 10 turns, power value is the boost amount
            duration = 10
            return self.status_effects_system.apply_effect(
                user, "shrinking", duration=duration, power=item.value
            )
        return False

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

    def _apply_teleport(
        self,
        item: Item,
        user: ComponentEntity,
        game_map: Optional["GameMap"] = None,
        entities: Optional[List[ComponentEntity]] = None,
    ) -> bool:
        """Apply teleport effect.

        Teleports the user to a random walkable location on the map.

        Args:
            item: Teleport scroll
            user: ComponentEntity to teleport
            game_map: Game map for finding valid locations
            entities: List of entities for collision checking

        Returns:
            True if teleportation succeeded
        """
        if game_map is None or entities is None:
            return False

        import random
        from roguelike.utils.position import Position

        # Try to find a random walkable position
        # Attempt up to 100 times to find a valid spot
        for _ in range(100):
            x = random.randint(0, game_map.width - 1)
            y = random.randint(0, game_map.height - 1)
            new_pos = Position(x, y)

            # Check if position is walkable and not occupied
            if game_map.is_walkable(new_pos):
                # Check for blocking entities
                blocked = False
                for entity in entities:
                    if entity.position == new_pos and entity.blocks_movement:
                        blocked = True
                        break

                if not blocked:
                    # Teleport successful
                    user.move_to(new_pos)
                    return True

        # Failed to find valid location after 100 attempts
        return False

    def _apply_magic_mapping(
        self,
        item: Item,
        user: ComponentEntity,
        fov_map: Optional["FOVMap"] = None,
    ) -> bool:
        """Apply magic mapping effect.

        Reveals the entire map to the user.

        Args:
            item: Magic mapping scroll
            user: ComponentEntity revealing map
            fov_map: FOV map to update

        Returns:
            True if map was revealed
        """
        if fov_map is None:
            return False

        # Reveal all tiles on the map
        fov_map.explored[:] = True
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

        Grants a temporary XP bonus for a duration.

        Args:
            item: Lucky coin
            user: ComponentEntity using coin

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            # Apply XP bonus effect
            # Duration is 20 turns, power value is the XP bonus percentage
            duration = 20
            return self.status_effects_system.apply_effect(
                user, "xp_bonus", duration=duration, power=item.value
            )
        return False

    def _apply_banana_peel(
        self,
        item: Item,
        user: ComponentEntity,
        target: Optional[ComponentEntity] = None,
    ) -> bool:
        """Apply banana peel effect.

        Throws banana peel at target, causing confusion.

        Args:
            item: Banana peel
            user: ComponentEntity throwing banana peel
            target: Target to confuse

        Returns:
            True if effect was applied
        """
        if not target or not target.is_alive:
            return False

        # Apply confusion to the target (they "slipped" on the banana peel)
        if self.status_effects_system:
            return self.status_effects_system.apply_effect(
                target, "confusion", duration=item.value, power=0
            )
        return False

    def _apply_rubber_chicken(
        self,
        item: Item,
        user: ComponentEntity,
        target: Optional[ComponentEntity] = None,
    ) -> bool:
        """Apply rubber chicken effect.

        Throws rubber chicken at target, dealing weak damage.

        Args:
            item: Rubber chicken
            user: ComponentEntity throwing rubber chicken
            target: Target to hit

        Returns:
            True if effect was applied
        """
        if not target or not target.is_alive:
            return False

        # Deal weak damage to the target
        from roguelike.components.health import HealthComponent

        health = target.get_component(HealthComponent)
        if health:
            health.take_damage(item.value)
            return True

        return False

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
