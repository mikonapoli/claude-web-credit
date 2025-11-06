"""Item system for handling item effects."""

from typing import List, Optional, TYPE_CHECKING

from roguelike.engine.events import EventBus, HealingEvent, ItemUseEvent
from roguelike.entities.actor import Actor
from roguelike.entities.item import Item, ItemType
from roguelike.systems.inventory import Inventory
from roguelike.systems.status_effects import StatusEffectsSystem

if TYPE_CHECKING:
    from roguelike.world.game_map import GameMap
    from roguelike.world.fov import FOVMap


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
        user: Actor,
        inventory: Inventory,
        target: Optional[Actor] = None,
        game_map: Optional["GameMap"] = None,
        fov_map: Optional["FOVMap"] = None,
    ) -> bool:
        """Use an item and apply its effects.

        Args:
            item: Item to use
            user: Actor using the item
            inventory: User's inventory
            target: Optional target actor for targeted items
            game_map: Optional game map for teleportation effects
            fov_map: Optional FOV map for magic mapping effects

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
        success = self._apply_item_effect(item, user, target, game_map, fov_map)

        # Remove item from inventory if used successfully
        if success:
            inventory.remove(item)

        return success

    def _apply_item_effect(
        self,
        item: Item,
        user: Actor,
        target: Optional[Actor] = None,
        game_map: Optional["GameMap"] = None,
        fov_map: Optional["FOVMap"] = None,
    ) -> bool:
        """Apply the effect of an item.

        Args:
            item: Item being used
            user: Actor using the item
            target: Optional target actor for targeted items
            game_map: Optional game map for teleportation effects
            fov_map: Optional FOV map for magic mapping effects

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
            return self._apply_teleport(item, user, game_map)
        elif item_type == ItemType.SCROLL_MAGIC_MAPPING:
            return self._apply_magic_mapping(item, user, fov_map)

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
        if self.status_effects_system:
            return self.status_effects_system.apply_effect(
                user, "speed", duration=item.value, power=0
            )
        return False

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
        if self.status_effects_system:
            # Gigantism increases power temporarily
            return self.status_effects_system.apply_effect(
                user, "gigantism", duration=item.value, power=3
            )
        return False

    def _apply_shrinking(self, item: Item, user: Actor) -> bool:
        """Apply shrinking effect.

        Args:
            item: Shrinking potion
            user: Actor to shrink

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            # Shrinking increases defense temporarily (harder to hit)
            return self.status_effects_system.apply_effect(
                user, "shrinking", duration=item.value, power=2
            )
        return False

    def _apply_fireball(self, item: Item, user: Actor, target: Optional[Actor] = None) -> bool:
        """Apply fireball effect.

        Args:
            item: Fireball scroll
            user: Actor casting fireball
            target: Target actor (required)

        Returns:
            True if effect was applied
        """
        # TODO: Implement AoE damage around target
        if not target or not target.is_alive:
            return False
        return True

    def _apply_lightning(self, item: Item, user: Actor, target: Optional[Actor] = None) -> bool:
        """Apply lightning effect.

        Args:
            item: Lightning scroll
            user: Actor casting lightning
            target: Target actor (required)

        Returns:
            True if effect was applied
        """
        # TODO: Implement single-target damage
        if not target or not target.is_alive:
            return False
        return True

    def _apply_confusion(self, item: Item, user: Actor, target: Optional[Actor] = None) -> bool:
        """Apply confusion effect.

        Args:
            item: Confusion scroll
            user: Actor casting confusion
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

    def _apply_teleport(self, item: Item, user: Actor, game_map: Optional["GameMap"]) -> bool:
        """Apply teleport effect.

        Args:
            item: Teleport scroll
            user: Actor to teleport
            game_map: Game map to find valid teleport location

        Returns:
            True if effect was applied
        """
        if not game_map:
            return False

        import random
        from roguelike.utils.position import Position

        # Find all walkable positions
        walkable_positions = []
        for y in range(game_map.height):
            for x in range(game_map.width):
                pos = Position(x, y)
                if game_map.is_walkable(pos):
                    walkable_positions.append(pos)

        if not walkable_positions:
            return False

        # Teleport to random walkable position
        new_position = random.choice(walkable_positions)
        user.position = new_position
        return True

    def _apply_magic_mapping(self, item: Item, user: Actor, fov_map: Optional["FOVMap"]) -> bool:
        """Apply magic mapping effect.

        Args:
            item: Magic mapping scroll
            user: Actor revealing map
            fov_map: FOV map to reveal

        Returns:
            True if effect was applied
        """
        if not fov_map:
            return False

        # Reveal entire map by marking all tiles as explored
        fov_map.explored[:] = True
        return True

    def _apply_coffee(self, item: Item, user: Actor) -> bool:
        """Apply coffee effect.

        Args:
            item: Coffee
            user: Actor drinking coffee

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            # Coffee gives a speed boost (like speed potion but shorter duration)
            return self.status_effects_system.apply_effect(
                user, "speed", duration=5, power=0
            )
        return False

    def _apply_lucky_coin(self, item: Item, user: Actor) -> bool:
        """Apply lucky coin effect.

        Args:
            item: Lucky coin
            user: Actor using coin

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            # Lucky coin gives XP boost for a duration
            # Power of 50 means 50% XP boost
            return self.status_effects_system.apply_effect(
                user, "lucky", duration=20, power=50
            )
        return False

    def _apply_banana_peel(self, item: Item, user: Actor) -> bool:
        """Apply banana peel effect.

        Args:
            item: Banana peel
            user: Actor using banana peel

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            # Banana peel is a comedic item - user slips and gets briefly confused
            return self.status_effects_system.apply_effect(
                user, "confusion", duration=3, power=0
            )
        return False

    def _apply_rubber_chicken(self, item: Item, user: Actor) -> bool:
        """Apply rubber chicken effect.

        Args:
            item: Rubber chicken
            user: Actor using rubber chicken

        Returns:
            True if effect was applied
        """
        if self.status_effects_system:
            # Rubber chicken is a silly weapon that gives a tiny power boost
            return self.status_effects_system.apply_effect(
                user, "rubber_chicken", duration=5, power=1
            )
        return False

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
