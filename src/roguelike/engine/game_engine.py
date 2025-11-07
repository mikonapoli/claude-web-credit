"""Main game engine."""

from typing import List, Optional

import tcod.event

from roguelike.components.entity import ComponentEntity
from roguelike.components.helpers import is_alive, is_monster
from roguelike.engine.events import (
    EventBus,
    CombatEvent,
    DeathEvent,
    LevelUpEvent,
    XPGainEvent,
    StatusEffectAppliedEvent,
    StatusEffectExpiredEvent,
    StatusEffectTickEvent,
)
from roguelike.entities.item import Item, ItemType
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.item_system import ItemSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.ui.input_handler import InputHandler
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
        player: ComponentEntity,
        entities: List[ComponentEntity] | None = None,
        level_system=None,
        stairs_pos: Optional[Position] = None,
    ):
        """Initialize the game engine.

        Args:
            game_map: The game map
            player: The player entity
            entities: List of other entities
            level_system: Optional dungeon level system for level transitions
            stairs_pos: Optional position of stairs down
        """
        self.game_map = game_map
        self.player = player
        self.entities = entities or []
        self.running = False
        self.message_log = MessageLog()
        self.active_targeted_item: Optional[Item] = None  # Track item being used with targeting
        self.level_system = level_system
        self.stairs_pos = stairs_pos
        self.current_dungeon_level = 1

        # Create event bus and systems
        self.event_bus = EventBus()
        self.combat_system = CombatSystem(self.event_bus)
        self.movement_system = MovementSystem(game_map)
        self.status_effects_system = StatusEffectsSystem(self.event_bus)
        self.item_system = ItemSystem(self.event_bus, self.status_effects_system)
        self.targeting_system = TargetingSystem()
        self.ai_system = AISystem(
            self.combat_system, self.movement_system, game_map, self.status_effects_system
        )

        # Subscribe to events for message logging
        self._setup_event_subscribers()

        # Create FOV map
        self.fov_map = FOVMap(game_map)
        self.fov_radius = 8

        # Create command executor
        from roguelike.commands import CommandExecutor

        self.command_executor = CommandExecutor(max_history=100)

        # Register monsters with AI system
        for entity in self.entities:
            if is_monster(entity):
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
                if is_monster(entity) and is_alive(entity):
                    died_from_effects = self.status_effects_system.process_effects(entity)
                    if died_from_effects:
                        self.combat_system.handle_death(entity, killed_by_player=False)
                        entity.blocks_movement = False

    def _transition_to_next_level(self) -> None:
        """Transition to the next dungeon level."""
        if not self.level_system:
            self.message_log.add_message("No more levels available!")
            return

        next_level = self.current_dungeon_level + 1

        # Check if next level exists
        if next_level > len(self.level_system.level_configs):
            self.message_log.add_message("You have reached the deepest level!")
            return

        # Generate new level
        game_map, rooms, monsters, stairs_pos = self.level_system.generate_level_with_monsters(next_level)

        # Update game state
        self.game_map = game_map
        self.stairs_pos = stairs_pos
        self.current_dungeon_level = next_level

        # Update map references in subsystems
        self.movement_system.game_map = game_map
        self.ai_system.game_map = game_map

        # Place player at start of first room
        self.player.position = rooms[0].center

        # Clear old entities and add new monsters
        self.entities.clear()
        self.entities.extend(monsters)

        # Re-register monsters with AI system
        self.ai_system.monster_ais.clear()
        for entity in self.entities:
            if is_monster(entity):
                self.ai_system.register_monster(entity)

        # Recreate FOV map for new level
        self.fov_map = FOVMap(self.game_map)
        self.fov_map.compute_fov(self.player.position, self.fov_radius)

        # Emit level transition event and log message
        level_name = self.level_system.level_configs[next_level].name
        self.message_log.add_message(f"You descend to level {next_level}: {level_name}")
        self.level_system.transition_to_level(next_level)

        # Note: InputHandler context will be updated in run() when it's recreated
        # or via update_context() if the handler persists across levels

    def run(self, renderer: Renderer) -> None:
        """Run the main game loop.

        Args:
            renderer: The renderer to use
        """
        self.running = True
        input_handler = InputHandler(
            player=self.player,
            entities=self.entities,
            game_map=self.game_map,
            fov_map=self.fov_map,
            fov_radius=self.fov_radius,
            combat_system=self.combat_system,
            movement_system=self.movement_system,
            ai_system=self.ai_system,
            status_effects_system=self.status_effects_system,
            targeting_system=self.targeting_system,
            message_log=self.message_log,
            stairs_pos=self.stairs_pos,
        )

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
            living_entities = [e for e in self.entities if not is_monster(e) or is_alive(e)]
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

            # Render health bars for monsters with health (entities that are monsters)
            monsters_to_render = [e for e in living_entities if is_monster(e)]
            renderer.render_health_bars(monsters_to_render, self.fov_map)

            # Render player stats panel in the top-right area of the map viewport
            stats_x = renderer.width - 35  # Position in top-right with more space
            stats_y = 0
            renderer.render_player_stats(
                self.player,
                x=stats_x,
                y=stats_y,
            )

            # Render status effects below stats (if any)
            effects_y = stats_y + 12  # Position below stats panel
            lines_rendered = renderer.render_status_effects(
                self.player,
                x=stats_x,
                y=effects_y,
            )

            # Render equipment below status effects (if any)
            equipment_y = effects_y + lines_rendered + (1 if lines_rendered > 0 else 0)
            renderer.render_equipment(
                self.player,
                x=stats_x,
                y=equipment_y,
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

            command = input_handler.get_command()
            if command:
                # Execute command through executor
                result = self.command_executor.execute(command)

                # Handle command results
                if result.should_quit:
                    self.running = False
                elif result.data:
                    # Handle special command results
                    if result.data.get("descend_stairs"):
                        self._transition_to_next_level()
                        # Update input handler with new level context
                        input_handler.update_context(
                            entities=self.entities,
                            game_map=self.game_map,
                            fov_map=self.fov_map,
                            stairs_pos=self.stairs_pos,
                        )
                    elif result.data.get("start_targeting"):
                        # Activate targeting mode in input handler
                        input_handler.set_targeting_mode(True)
                    elif result.data.get("targeting_select"):
                        # Targeting selection made - exit targeting mode
                        input_handler.set_targeting_mode(False)

                        # Use confusion scroll on the selected target (test feature for 'C' key)
                        target = result.data.get("target")
                        if target:
                            # Find first confusion scroll in inventory
                            from roguelike.entities.item import ItemType
                            confusion_scroll = None
                            for item in self.player.inventory.items:
                                if hasattr(item, 'item_type') and item.item_type == ItemType.SCROLL_CONFUSION:
                                    confusion_scroll = item
                                    break

                            if confusion_scroll:
                                # Use the confusion scroll on the target
                                success = self.item_system.use_item(
                                    confusion_scroll,
                                    self.player,
                                    self.player.inventory,
                                    target=target
                                )
                                if success:
                                    self.message_log.add_message(f"You confuse the {target.name}!")
                                    # Process turn after successful item use
                                    # This allows enemies to act and status effects to tick
                                    self._process_turn_after_action()
                                else:
                                    self.message_log.add_message("The confusion scroll failed!")
                            else:
                                self.message_log.add_message("No confusion scroll in inventory!")
                    elif result.data.get("targeting_cancel"):
                        # Targeting cancelled - exit targeting mode
                        input_handler.set_targeting_mode(False)

        renderer.close()
