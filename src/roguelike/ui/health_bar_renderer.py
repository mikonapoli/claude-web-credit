"""Health bar rendering for entities."""

from typing import Tuple

import tcod.console


class HealthBarRenderer:
    """Renders health bars above entities."""

    def __init__(self, bar_width: int = 10):
        """Initialize health bar renderer.

        Args:
            bar_width: Width of the health bar in characters
        """
        self.bar_width = bar_width
        self.empty_char = "░"  # Light shade for empty part
        self.filled_char = "█"  # Full block for filled part

    def calculate_fill_percentage(self, hp: int, max_hp: int) -> float:
        """Calculate what percentage of the health bar should be filled.

        Args:
            hp: Current hit points
            max_hp: Maximum hit points

        Returns:
            Fill percentage as a float between 0.0 and 1.0
        """
        if max_hp <= 0:
            return 0.0
        return max(0.0, min(1.0, hp / max_hp))

    def get_health_color(self, fill_percentage: float) -> Tuple[int, int, int]:
        """Get the color for the health bar based on fill percentage.

        Args:
            fill_percentage: Health percentage (0.0 to 1.0)

        Returns:
            RGB color tuple
        """
        if fill_percentage >= 0.6:
            return (0, 255, 0)  # Green for healthy
        elif fill_percentage >= 0.25:
            return (255, 255, 0)  # Yellow for injured
        else:
            return (255, 0, 0)  # Red for critical

    def render(
        self,
        console: tcod.console.Console,
        x: int,
        y: int,
        hp: int,
        max_hp: int,
    ) -> None:
        """Render a health bar at the specified position.

        Args:
            console: Console to render to
            x: X position (left edge of bar)
            y: Y position
            hp: Current hit points
            max_hp: Maximum hit points
        """
        fill_percentage = self.calculate_fill_percentage(hp, max_hp)
        color = self.get_health_color(fill_percentage)

        # Calculate how many characters should be filled
        filled_width = int(fill_percentage * self.bar_width)

        # Render filled portion
        for i in range(filled_width):
            console.print(x + i, y, self.filled_char, fg=color)

        # Render empty portion
        empty_color = (100, 100, 100)  # Dark gray
        for i in range(filled_width, self.bar_width):
            console.print(x + i, y, self.empty_char, fg=empty_color)
