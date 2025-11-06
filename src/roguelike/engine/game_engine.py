"""Main game engine."""

from typing import List, Optional

import tcod.event

from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent, EquipmentSlot, EquipmentStats
from roguelike.components.inventory import InventoryComponent
from roguelike.engine.events import (
    EventBus,
    CombatEvent,
    DeathEvent,
    EquipEvent,
    LevelUpEvent,
    UnequipEvent,
    XPGainEvent,
    StatusEffectAppliedEvent,
    StatusEffectExpiredEvent,
    StatusEffectTickEvent,
)
from roguelike.entities.actor import Actor
from roguelike.entities.entity import Entity
from roguelike.entities.item import Item, ItemType
from roguelike.entities.monster import Monster
from roguelike.entities.player import Player
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.equipment_system import EquipmentSystem
from roguelike.systems.item_system import ItemSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.systems.turn_manager import TurnManager
from roguelike.ui.input_handler import Action, InputHandler
from roguelike.ui.message_log import MessageLog
from roguelike.ui.renderer import Renderer
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class GameEngine:
    """Main game engine that manages the game loop."""

    def __init__(
        self,
        game_map: GameMap,
        player: Player,
        entities: List[Entity] | None = None,
    ):
        """Initialize the game engine.

        Args:
            game_map: The game map
            player: The player entity
            entities: List of other entities
        """
        self.game_map = game_map
        self.player = player
        self.entities = entities or []
        self.running = False
        self.message_log = MessageLog()
        self.active_targeted_item: Optional[Item] = None  # Track item being used with targeting
        self.equipment_menu_active = False  # Track if equipment menu is shown
        self.unequip_menu_active = False  # Track if unequip menu is shown

        # Create event bus and systems
        self.event_bus = EventBus()
        self.combat_system = CombatSystem(self.event_bus)
        self.movement_system = MovementSystem(game_map)
        self.status_effects_system = StatusEffectsSystem(self.event_bus)
        self.equipment_system = EquipmentSystem(self.event_bus)
        self.item_system = ItemSystem(self.event_bus, self.status_effects_system)
        self.targeting_system = TargetingSystem()
        self.ai_system = AISystem(
            self.combat_system, self.movement_system, game_map, self.status_effects_system
        )
        self.turn_manager = TurnManager(
            self.combat_system, self.movement_system, self.ai_system, self.status_effects_system
        )

        # Subscribe to events for message logging
        self._setup_event_subscribers()

        # Create FOV map
        self.fov_map = FOVMap(game_map)
        self.fov_radius = 8

        # Register monsters with AI system
        for entity in self.entities:
            if isinstance(entity, Monster):
                self.ai_system.register_monster(entity)

        # Compute initial FOV
        self.fov_map.compute_fov(self.player.position, self.fov_radius)

    def _setup_event_subscribers(self) -> None:
        """Set up event subscribers for message logging."""
        self.event_bus.subscribe("combat", self._on_combat_event)
        self.event_bus.subscribe("death", self._on_death_event)
        self.event_bus.subscribe("xp_gain", self._on_xp_gain_event)
        self.event_bus.subscribe("level_up", self._on_level_up_event)
        self.event_bus.subscribe("status_effect_applied", self._on_status_effect_applied)
        self.event_bus.subscribe("status_effect_expired", self._on_status_effect_expired)
        self.event_bus.subscribe("status_effect_tick", self._on_status_effect_tick)
        self.event_bus.subscribe("equip", self._on_equip_event)
        self.event_bus.subscribe("unequip", self._on_unequip_event)

    def _on_combat_event(self, event: CombatEvent) -> None:
        """Handle combat event."""
        self.message_log.add_message(
            f"{event.attacker_name} attacks {event.defender_name} "
            f"for {event.damage} damage!"
        )

    def _on_death_event(self, event: DeathEvent) -> None:
        """Handle death event."""
        self.message_log.add_message(f"{event.entity_name} dies!")

    def _on_xp_gain_event(self, event: XPGainEvent) -> None:
        """Handle XP gain event."""
        self.message_log.add_message(f"You gain {event.xp_gained} XP!")

    def _on_level_up_event(self, event: LevelUpEvent) -> None:
        """Handle level up event."""
        self.message_log.add_message(
            f"You advance to level {event.new_level}!"
        )

    def _on_status_effect_applied(self, event: StatusEffectAppliedEvent) -> None:
        """Handle status effect applied event."""
        effect_name = event.effect_type.capitalize()
        self.message_log.add_message(
            f"{event.entity_name} is affected by {effect_name} for {event.duration} turns!"
        )

    def _on_status_effect_expired(self, event: StatusEffectExpiredEvent) -> None:
        """Handle status effect expired event."""
        effect_name = event.effect_type.capitalize()
        self.message_log.add_message(
            f"{event.entity_name}'s {effect_name} effect has worn off."
        )

    def _on_status_effect_tick(self, event: StatusEffectTickEvent) -> None:
        """Handle status effect tick event."""
        # Only show messages for poison (damage-dealing effects)
        if event.effect_type == "poison" and event.power > 0:
            self.message_log.add_message(
                f"{event.entity_name} takes {event.power} poison damage!"
            )

    def _on_equip_event(self, event: EquipEvent) -> None:
        """Handle equip event."""
        bonuses = []
        if event.power_bonus != 0:
            bonuses.append(f"+{event.power_bonus} power" if event.power_bonus > 0 else f"{event.power_bonus} power")
        if event.defense_bonus != 0:
            bonuses.append(f"+{event.defense_bonus} defense" if event.defense_bonus > 0 else f"{event.defense_bonus} defense")
        if event.max_hp_bonus != 0:
            bonuses.append(f"+{event.max_hp_bonus} HP" if event.max_hp_bonus > 0 else f"{event.max_hp_bonus} HP")

        bonus_text = f" ({', '.join(bonuses)})" if bonuses else ""
        self.message_log.add_message(
            f"{event.entity_name} equipped {event.item_name}{bonus_text}"
        )

    def _on_unequip_event(self, event: UnequipEvent) -> None:
        """Handle unequip event."""
        self.message_log.add_message(
            f"{event.entity_name} unequipped {event.item_name}"
        )

    def _process_turn_after_action(self) -> None:
        """Process turn effects after an action that consumes a turn.

        This handles status effects and AI turns without requiring
        the full turn manager flow.
        """
        # Process status effects on player
        if self.status_effects_system:
            player_died = self.status_effects_system.process_effects(self.player)

            if player_died:
                # Handle death from status effects
                self.combat_system.handle_death(self.player, killed_by_player=False)
                self.player.blocks_movement = False
                self.running = False  # Game over
                return

        # Process enemy turns
        player_died = self.ai_system.process_turns(self.player, self.entities)
        if player_died:
            self.running = False  # Game over
            return

        # Process status effects on monsters
        if self.status_effects_system:
            for entity in self.entities:
                if isinstance(entity, Monster) and entity.is_alive:
                    died_from_effects = self.status_effects_system.process_effects(entity)
                    if died_from_effects:
                        self.combat_system.handle_death(entity, killed_by_player=False)
                        entity.blocks_movement = False

    def _start_confusion_targeting(self, input_handler: InputHandler) -> None:
        """Start targeting mode for confusion scroll.

        Args:
            input_handler: Input handler to set targeting mode
        """
        # Check if player has a confusion scroll in inventory
        confusion_scroll = None
        for item in self.player.inventory.items:
            if item.item_type == ItemType.SCROLL_CONFUSION:
                confusion_scroll = item
                break

        if not confusion_scroll:
            self.message_log.add_message("No confusion scroll in inventory!")
            return

        # Get all living monsters that are visible
        monsters = [
            e for e in self.entities
            if isinstance(e, Monster) and e.is_alive and self.fov_map.is_visible(e.position)
        ]

        if not monsters:
            self.message_log.add_message("No visible targets!")
            return

        # Start targeting with max range of 10
        max_range = 10
        if self.targeting_system.start_targeting(
            self.player.position, max_range, monsters,
            self.game_map.width, self.game_map.height
        ):
            self.active_targeted_item = confusion_scroll
            input_handler.set_targeting_mode(True)
            self.message_log.add_message(
                "Select a target (Tab to cycle, Enter to select, Escape to cancel)"
            )
        else:
            self.message_log.add_message("No targets in range!")

    def _handle_targeting_action(self, action: Action, input_handler: InputHandler) -> None:
        """Handle actions while in targeting mode.

        Args:
            action: The action to handle
            input_handler: Input handler to control targeting mode
        """
        # Map movement directions
        movement_map = {
            Action.MOVE_UP: (0, -1),
            Action.MOVE_DOWN: (0, 1),
            Action.MOVE_LEFT: (-1, 0),
            Action.MOVE_RIGHT: (1, 0),
            Action.MOVE_UP_LEFT: (-1, -1),
            Action.MOVE_UP_RIGHT: (1, -1),
            Action.MOVE_DOWN_LEFT: (-1, 1),
            Action.MOVE_DOWN_RIGHT: (1, 1),
        }

        if action in movement_map:
            # Move cursor
            dx, dy = movement_map[action]
            self.targeting_system.move_cursor(dx, dy)

        elif action == Action.TARGETING_CYCLE_NEXT:
            # Cycle to next target
            self.targeting_system.cycle_target(1)

        elif action == Action.TARGETING_CYCLE_PREV:
            # Cycle to previous target
            self.targeting_system.cycle_target(-1)

        elif action == Action.TARGETING_SELECT:
            # Select target and use stored targeted item
            target = self.targeting_system.select_target()
            input_handler.set_targeting_mode(False)

            if target and self.active_targeted_item:
                # Use the stored item on the target
                success = self.item_system.use_item(
                    self.active_targeted_item, self.player, self.player.inventory, target=target
                )

                if success:
                    self.message_log.add_message(
                        f"You confuse the {target.name} for 10 turns!"
                    )
                    # Item use consumes a turn - process turn effects
                    self._process_turn_after_action()
                else:
                    self.message_log.add_message("Failed to confuse target!")

                # Clear the active item reference
                self.active_targeted_item = None
            elif not target:
                self.message_log.add_message("No target selected!")
                self.active_targeted_item = None
            else:
                self.message_log.add_message("No item to use!")
                self.active_targeted_item = None

        elif action == Action.TARGETING_CANCEL:
            # Cancel targeting
            self.targeting_system.cancel_targeting()
            input_handler.set_targeting_mode(False)
            self.active_targeted_item = None
            self.message_log.add_message("Targeting cancelled.")

    def _show_equipment_menu(self) -> None:
        """Show equipment menu with items that can be equipped."""
        # Check if player has component-based equipment
        if not isinstance(self.player, ComponentEntity):
            self.message_log.add_message("Equipment system not available for this player type.")
            return

        inventory = self.player.get_component(InventoryComponent)
        if not inventory:
            self.message_log.add_message("No inventory available.")
            return

        # Get equipment items from inventory
        equippable_items = [
            item for item in inventory.get_items()
            if isinstance(item, ComponentEntity) and item.get_component(EquipmentStats)
        ]

        if not equippable_items:
            self.message_log.add_message("No equipment items in inventory.")
            return

        # Show first item as example (in a real implementation, you'd have a menu UI)
        item = equippable_items[0]
        stats = item.get_component(EquipmentStats)
        if stats:
            self._equip_item(item)

    def _equip_item(self, item: ComponentEntity) -> None:
        """Equip an item from inventory.

        Args:
            item: Item to equip
        """
        if not isinstance(self.player, ComponentEntity):
            return

        equipment_comp = self.player.get_component(EquipmentComponent)
        inventory = self.player.get_component(InventoryComponent)

        if not equipment_comp or not inventory:
            self.message_log.add_message("Cannot equip item.")
            return

        # Check if item is in inventory
        if item not in inventory.get_items():
            self.message_log.add_message("Item not in inventory.")
            return

        # Remove item from inventory
        inventory.remove_item(item)

        # Equip the item (this handles replacing previous equipment)
        previous_item = self.equipment_system.equip_item(self.player, item)

        # If there was a previously equipped item, put it back in inventory
        if previous_item:
            inventory.add_item(previous_item)

    def _show_unequip_menu(self) -> None:
        """Show unequip menu with currently equipped items."""
        if not isinstance(self.player, ComponentEntity):
            self.message_log.add_message("Equipment system not available for this player type.")
            return

        equipment_comp = self.player.get_component(EquipmentComponent)
        if not equipment_comp:
            self.message_log.add_message("No equipment component.")
            return

        equipped_items = equipment_comp.get_all_equipped()
        if not equipped_items:
            self.message_log.add_message("No items equipped.")
            return

        # Unequip first equipped item as example
        first_slot = next(iter(equipped_items.keys()))
        self._unequip_item(first_slot)

    def _unequip_item(self, slot: EquipmentSlot) -> None:
        """Unequip an item to inventory.

        Args:
            slot: Equipment slot to unequip from
        """
        if not isinstance(self.player, ComponentEntity):
            return

        equipment_comp = self.player.get_component(EquipmentComponent)
        inventory = self.player.get_component(InventoryComponent)

        if not equipment_comp or not inventory:
            self.message_log.add_message("Cannot unequip item.")
            return

        # Check if slot has an item
        if equipment_comp.is_slot_empty(slot):
            self.message_log.add_message("No item in that slot.")
            return

        # Check if inventory has space
        if inventory.is_full():
            self.message_log.add_message("Inventory is full!")
            return

        # Unequip the item
        item = self.equipment_system.unequip_item(self.player, slot)

        if item:
            # Add unequipped item to inventory
            inventory.add_item(item)

    def run(self, renderer: Renderer) -> None:
        """Run the main game loop.

        Args:
            renderer: The renderer to use
        """
        self.running = True
        input_handler = InputHandler()

        # Message log display configuration
        # Use the map's actual height for viewport, message log fills remaining space
        map_viewport_height = self.game_map.height
        message_log_y = self.game_map.height
        message_log_height = renderer.height - self.game_map.height

        while self.running:
            # Render
            renderer.clear()
            renderer.render_map(self.game_map, self.fov_map, max_height=map_viewport_height)
            # Only render living monsters
            living_entities = [e for e in self.entities if not isinstance(e, Monster) or e.is_alive]
            renderer.render_entities(living_entities, self.fov_map, max_height=map_viewport_height)
            renderer.render_entity(self.player, self.fov_map, max_height=map_viewport_height)
            # Render message log at bottom of screen
            renderer.render_message_log(
                self.message_log,
                x=0,
                y=message_log_y,
                width=renderer.width,
                height=message_log_height
            )

            # Render health bars only for Actors (entities with health, excluding player)
            actors_to_render = [e for e in living_entities if isinstance(e, Actor)]
            renderer.render_health_bars(actors_to_render, self.fov_map)

            # Render player stats as text in the top-right area of the map viewport
            renderer.render_player_stats(
                self.player,
                x=renderer.width - 20,  # Position in top-right
                y=0,
            )

            # Render equipped items below player stats
            renderer.render_equipped_items(
                self.player,
                x=renderer.width - 20,
                y=2,
            )

            # Render targeting cursor if in targeting mode
            if self.targeting_system.is_active:
                cursor_pos = self.targeting_system.get_cursor_position()
                target = self.targeting_system.get_current_target()
                target_name = target.name if target else None
                if cursor_pos:
                    renderer.render_targeting_cursor(cursor_pos, target_name)

            renderer.present()

            # Handle input
            for event in tcod.event.wait():
                input_handler.dispatch(event)

            action = input_handler.get_action()
            if action:
                # Handle targeting mode actions
                if self.targeting_system.is_active:
                    self._handle_targeting_action(action, input_handler)
                # Handle equipment actions
                elif action == Action.EQUIP:
                    self._show_equipment_menu()
                elif action == Action.UNEQUIP:
                    self._show_unequip_menu()
                # Handle TEST_CONFUSION action to start targeting
                elif action == Action.TEST_CONFUSION:
                    self._start_confusion_targeting(input_handler)
                # Normal game actions
                else:
                    self.running = self.turn_manager.process_turn(
                        action,
                        self.player,
                        self.entities,
                        self.game_map,
                        self.fov_map,
                        self.fov_radius,
                    )

        renderer.close()
