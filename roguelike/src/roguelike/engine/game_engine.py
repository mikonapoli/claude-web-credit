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

    def handle_action(self, action: Action) -> bool:
        """Handle a player action.

        Args:
            action: Action to handle

        Returns:
            True if the action consumed a turn
        """
        if action == Action.QUIT:
            self.running = False
            return False

        if action == Action.WAIT:
            return True

        # Movement actions
        movement_map = {
            Action.MOVE_UP: (0, -1),
            Action.MOVE_DOWN: (0, 1),
            Action.MOVE_LEFT: (-1, 0),
            Action.MOVE_RIGHT: (1, 0),
            Action.MOVE_UP_LEFT: (-1, -1),
            Action.MOVE_UP_RIGHT: (1, -1),
            Action.MOVE_DOWN_LEFT: (-1, -1),
            Action.MOVE_DOWN_RIGHT: (1, 1),
        }

        if action in movement_map:
            dx, dy = movement_map[action]
            return self.try_move_player(dx, dy)

        return False

    def try_move_player(self, dx: int, dy: int) -> bool:
        """Try to move the player.

        Args:
            dx: X offset
            dy: Y offset

        Returns:
            True if movement was successful (consumes turn)
        """
        new_pos = Position(
            self.player.position.x + dx,
            self.player.position.y + dy
        )

        # Check for blocking entity at destination
        blocking_entity = self.movement_system.get_blocking_entity(new_pos, self.entities)

        if blocking_entity:
            # If it's a living monster, attack it
            if isinstance(blocking_entity, Monster) and blocking_entity.is_alive:
                # Use combat system to resolve attack
                defender_died = self.combat_system.resolve_attack(self.player, blocking_entity)

                if defender_died:
                    # Handle death and award XP
                    self.combat_system.handle_death(blocking_entity, killed_by_player=True)
                    self.combat_system.award_xp(self.player, blocking_entity.xp_value)

                return True  # Attack consumes turn
            # Other blocking entity (not attackable)
            return False

        # Try to move player
        if self.movement_system.move_entity(self.player, dx, dy, self.entities):
            # Update FOV after successful movement
            self.movement_system.update_fov(self.fov_map, self.player.position, self.fov_radius)
            return True

        return False

    def process_enemy_turns(self) -> None:
        """Process all enemy turns."""
        player_died = self.ai_system.process_turns(self.player, self.entities)
        if player_died:
            self.running = False  # Game over

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
            renderer.present()

            # Handle input
            for event in tcod.event.wait():
                input_handler.dispatch(event)

            action = input_handler.get_action()
            if action:
                turn_taken = self.handle_action(action)
                if turn_taken and self.player.is_alive:
                    self.process_enemy_turns()

        renderer.close()
