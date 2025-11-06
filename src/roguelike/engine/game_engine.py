"""Main game engine."""

from typing import List, Optional

import tcod.event

from roguelike.engine.events import (
    EventBus,
    CombatEvent,
    CraftingAttemptEvent,
    DeathEvent,
    LevelUpEvent,
    RecipeDiscoveredEvent,
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
from roguelike.data.recipe_loader import RecipeLoader
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.crafting import CraftingSystem
from roguelike.systems.item_system import ItemSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.systems.turn_manager import TurnManager
from roguelike.commands.crafting_commands import CraftItemsCommand
from roguelike.ui.crafting_menu import CraftingMenu
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
        self.crafting_menu: Optional[CraftingMenu] = None  # Track active crafting menu

        # Create event bus and systems
        self.event_bus = EventBus()
        self.combat_system = CombatSystem(self.event_bus)
        self.movement_system = MovementSystem(game_map)
        self.status_effects_system = StatusEffectsSystem(self.event_bus)
        self.item_system = ItemSystem(self.event_bus, self.status_effects_system)
        self.targeting_system = TargetingSystem()
        self.recipe_loader = RecipeLoader()
        self.crafting_system = CraftingSystem(self.recipe_loader, self.event_bus)
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
        self.event_bus.subscribe("crafting_attempt", self._on_crafting_attempt)
        self.event_bus.subscribe("recipe_discovered", self._on_recipe_discovered)

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

    def _on_crafting_attempt(self, event: CraftingAttemptEvent) -> None:
        """Handle crafting attempt event."""
        if event.success:
            self.message_log.add_message(
                f"You craft {event.result_name}!"
            )
        else:
            ingredient_list = ", ".join(event.ingredient_names)
            self.message_log.add_message(
                f"No recipe found for: {ingredient_list}"
            )

    def _on_recipe_discovered(self, event: RecipeDiscoveredEvent) -> None:
        """Handle recipe discovered event."""
        self.message_log.add_message(
            f"New recipe discovered: {event.recipe_name}!"
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

    def _open_crafting_menu(self, renderer: Renderer) -> None:
        """Open the crafting menu.

        Args:
            renderer: Renderer for getting console dimensions
        """
        self.crafting_menu = CraftingMenu(
            crafter=self.player,
            crafting_system=self.crafting_system,
            console_width=renderer.width,
            console_height=renderer.height,
        )
        self.message_log.add_message("Opened crafting menu (R to close)")

    def _close_crafting_menu(self) -> None:
        """Close the crafting menu."""
        self.crafting_menu = None
        self.message_log.add_message("Closed crafting menu")

    def _handle_crafting_menu_action(self, key: int) -> None:
        """Handle actions while in crafting menu.

        Args:
            key: Key code
        """
        if not self.crafting_menu:
            return

        action = self.crafting_menu.handle_key(key)

        if action == "close":
            self._close_crafting_menu()
        elif action == "craft":
            # Attempt to craft with selected ingredients
            selected = self.crafting_menu.selected_ingredients

            if not selected:
                self.message_log.add_message("No ingredients selected!")
                return

            # Create and execute craft command
            craft_command = CraftItemsCommand(
                crafter=self.player,
                ingredients=selected,
                crafting_system=self.crafting_system,
                entities=self.entities,
            )

            result = craft_command.execute()

            if result.success:
                # Clear selection after successful craft
                self.crafting_menu.clear_selection()
                # Process turn effects
                self._process_turn_after_action()
            # Messages are handled by event system

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

            # Render targeting cursor if in targeting mode
            if self.targeting_system.is_active:
                cursor_pos = self.targeting_system.get_cursor_position()
                target = self.targeting_system.get_current_target()
                target_name = target.name if target else None
                if cursor_pos:
                    renderer.render_targeting_cursor(cursor_pos, target_name)

            # Render crafting menu if open
            if self.crafting_menu:
                self.crafting_menu.render(renderer.console)

            renderer.present()

            # Handle input
            for event in tcod.event.wait():
                # Handle crafting menu input separately
                if self.crafting_menu and isinstance(event, tcod.event.KeyDown):
                    self._handle_crafting_menu_action(event.sym)
                else:
                    input_handler.dispatch(event)

            action = input_handler.get_action()
            if action:
                # Handle crafting menu open action
                if action == Action.CRAFT:
                    if self.crafting_menu:
                        self._close_crafting_menu()
                    else:
                        self._open_crafting_menu(renderer)
                # Handle targeting mode actions
                elif self.targeting_system.is_active:
                    self._handle_targeting_action(action, input_handler)
                # Handle TEST_CONFUSION action to start targeting
                elif action == Action.TEST_CONFUSION:
                    self._start_confusion_targeting(input_handler)
                # Normal game actions (only if not in crafting menu)
                elif not self.crafting_menu:
                    self.running = self.turn_manager.process_turn(
                        action,
                        self.player,
                        self.entities,
                        self.game_map,
                        self.fov_map,
                        self.fov_radius,
                    )

        renderer.close()
