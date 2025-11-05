"""Main game engine."""

from typing import List

import tcod.event

from roguelike.engine.events import EventBus, CombatEvent, DeathEvent, LevelUpEvent, XPGainEvent
from roguelike.entities.entity import Entity
from roguelike.entities.monster import Monster
from roguelike.entities.player import Player
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.turn_manager import TurnManager
from roguelike.ui.input_handler import Action, InputHandler
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
        self.message_log: List[str] = []

        # Create event bus and systems
        self.event_bus = EventBus()
        self.combat_system = CombatSystem(self.event_bus)
        self.movement_system = MovementSystem(game_map)
        self.ai_system = AISystem(self.combat_system, self.movement_system, game_map)
        self.turn_manager = TurnManager(self.combat_system, self.movement_system, self.ai_system)

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

    def _on_combat_event(self, event: CombatEvent) -> None:
        """Handle combat event."""
        self.message_log.append(
            f"{event.attacker_name} attacks {event.defender_name} "
            f"for {event.damage} damage!"
        )

    def _on_death_event(self, event: DeathEvent) -> None:
        """Handle death event."""
        self.message_log.append(f"{event.entity_name} dies!")

    def _on_xp_gain_event(self, event: XPGainEvent) -> None:
        """Handle XP gain event."""
        self.message_log.append(f"You gain {event.xp_gained} XP!")

    def _on_level_up_event(self, event: LevelUpEvent) -> None:
        """Handle level up event."""
        self.message_log.append(
            f"You advance to level {event.new_level}!"
        )


    def run(self, renderer: Renderer) -> None:
        """Run the main game loop.

        Args:
            renderer: The renderer to use
        """
        self.running = True
        input_handler = InputHandler()

        while self.running:
            # Render
            renderer.clear()
            renderer.render_map(self.game_map, self.fov_map)
            # Only render living monsters
            living_entities = [e for e in self.entities if not isinstance(e, Monster) or e.is_alive]
            renderer.render_entities(living_entities, self.fov_map)
            renderer.render_entity(self.player, self.fov_map)

            # Render health bars for all living entities with health
            renderer.render_health_bars(living_entities, self.fov_map)
            renderer.render_health_bar(self.player, self.fov_map)

            renderer.present()

            # Handle input
            for event in tcod.event.wait():
                input_handler.dispatch(event)

            action = input_handler.get_action()
            if action:
                self.running = self.turn_manager.process_turn(
                    action,
                    self.player,
                    self.entities,
                    self.game_map,
                    self.fov_map,
                    self.fov_radius,
                )

        renderer.close()
