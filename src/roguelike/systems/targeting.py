"""Targeting system for selecting entities at range."""

from typing import List, Optional

from roguelike.entities.actor import Actor
from roguelike.utils.position import Position


class TargetingSystem:
    """Manages targeting cursor and target selection."""

    def __init__(self):
        """Initialize the targeting system."""
        self.is_active: bool = False
        self.cursor_position: Optional[Position] = None
        self.origin: Optional[Position] = None
        self.max_range: int = 0
        self.valid_targets: List[Actor] = []
        self.current_target_index: int = 0
        self.map_width: int = 0
        self.map_height: int = 0

    def start_targeting(
        self, origin: Position, max_range: int, valid_targets: List[Actor],
        map_width: int, map_height: int
    ) -> bool:
        """Start targeting mode.

        Args:
            origin: Starting position (usually player position)
            max_range: Maximum targeting range
            valid_targets: List of valid target actors
            map_width: Width of the game map
            map_height: Height of the game map

        Returns:
            True if there are valid targets, False otherwise
        """
        # Filter targets by range and alive status
        targets_in_range = [
            target
            for target in valid_targets
            if target.is_alive
            and origin.manhattan_distance_to(target.position) <= max_range
        ]

        if not targets_in_range:
            return False

        self.is_active = True
        self.origin = origin
        self.max_range = max_range
        self.map_width = map_width
        self.map_height = map_height
        self.valid_targets = targets_in_range
        self.current_target_index = 0
        self.cursor_position = targets_in_range[0].position

        return True

    def get_cursor_position(self) -> Optional[Position]:
        """Get current cursor position.

        Returns:
            Current cursor position or None if not targeting
        """
        return self.cursor_position

    def get_valid_targets(self) -> List[Actor]:
        """Get list of valid targets.

        Returns:
            List of valid target actors
        """
        return self.valid_targets

    def get_current_target(self) -> Optional[Actor]:
        """Get the actor at the current cursor position.

        Returns:
            Actor at cursor position or None
        """
        if not self.is_active or not self.cursor_position:
            return None

        for target in self.valid_targets:
            if target.position == self.cursor_position:
                return target

        return None

    def cycle_target(self, direction: int = 1) -> None:
        """Cycle to next/previous target.

        Args:
            direction: 1 for next, -1 for previous
        """
        if not self.is_active or not self.valid_targets:
            return

        self.current_target_index = (
            self.current_target_index + direction
        ) % len(self.valid_targets)
        self.cursor_position = self.valid_targets[self.current_target_index].position

    def move_cursor(self, dx: int, dy: int) -> None:
        """Move cursor by delta.

        Args:
            dx: X delta
            dy: Y delta
        """
        if not self.is_active or not self.cursor_position or not self.origin:
            return

        new_position = Position(
            self.cursor_position.x + dx, self.cursor_position.y + dy
        )

        # Check if new position is within map bounds
        if new_position.x < 0 or new_position.x >= self.map_width:
            return
        if new_position.y < 0 or new_position.y >= self.map_height:
            return

        # Check if new position is within range
        if self.origin.manhattan_distance_to(new_position) <= self.max_range:
            self.cursor_position = new_position

    def select_target(self) -> Optional[Actor]:
        """Confirm target selection.

        Returns:
            Selected target actor or None
        """
        target = self.get_current_target()
        self.cancel_targeting()
        return target

    def cancel_targeting(self) -> None:
        """Cancel targeting mode."""
        self.is_active = False
        self.cursor_position = None
        self.origin = None
        self.max_range = 0
        self.valid_targets = []
        self.current_target_index = 0
