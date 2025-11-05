"""Main game engine."""

from typing import List

import tcod.event

from roguelike.entities.entity import Entity
from roguelike.entities.monster import Monster
from roguelike.entities.player import Player
from roguelike.systems.ai import MonsterAI
from roguelike.systems.combat import attack
from roguelike.systems.experience import apply_level_up, check_level_up
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

        # Create FOV map
        self.fov_map = FOVMap(game_map)
        self.fov_radius = 8

        # Create AI for monsters
        self.monster_ais: dict[Monster, MonsterAI] = {}
        for entity in self.entities:
            if isinstance(entity, Monster):
                self.monster_ais[entity] = MonsterAI(entity)

        # Compute initial FOV
        self.fov_map.compute_fov(self.player.position, self.fov_radius)

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

        # Check if destination is walkable
        if not self.game_map.is_walkable(new_pos):
            return False

        # Check if any entity blocks movement at destination
        for entity in self.entities:
            if entity.position == new_pos and entity.blocks_movement:
                # If it's a monster, attack it
                if isinstance(entity, Monster) and entity.is_alive:
                    result = attack(self.player, entity)
                    self.message_log.append(
                        f"{result.attacker_name} attacks {result.defender_name} "
                        f"for {result.damage} damage!"
                    )
                    if result.defender_died:
                        self.message_log.append(f"{result.defender_name} dies!")
                        # Award XP
                        self.player.xp += entity.xp_value
                        self.message_log.append(f"You gain {entity.xp_value} XP!")
                        # Check for level up
                        if check_level_up(self.player.xp, self.player.level):
                            level_result = apply_level_up(
                                self.player,
                                {"hp": 20, "power": 1, "defense": 1}
                            )
                            self.message_log.append(
                                f"You advance to level {level_result.new_level}!"
                            )
                    return True  # Attack consumes turn
                return False

        # Move is valid
        self.player.move(dx, dy)
        # Recompute FOV after movement
        self.fov_map.compute_fov(self.player.position, self.fov_radius)
        return True

    def process_enemy_turns(self) -> None:
        """Process all enemy turns."""
        for entity in self.entities:
            if not isinstance(entity, Monster) or not entity.is_alive:
                continue

            ai = self.monster_ais.get(entity)
            if not ai:
                continue

            # Get all living entities for blocking checks
            living_entities = [e for e in self.entities if isinstance(e, Monster) and e.is_alive]
            living_entities.append(self.player)

            new_pos = ai.take_turn(self.player, self.game_map, living_entities)

            if new_pos:
                # Check if adjacent to player (attack)
                if new_pos.manhattan_distance_to(self.player.position) <= 1:
                    result = attack(entity, self.player)
                    self.message_log.append(
                        f"{result.attacker_name} attacks {result.defender_name} "
                        f"for {result.damage} damage!"
                    )
                    if result.defender_died:
                        self.message_log.append(f"{result.defender_name} dies!")
                        self.running = False  # Player died, game over
                else:
                    # Move to new position
                    entity.move_to(new_pos)

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
