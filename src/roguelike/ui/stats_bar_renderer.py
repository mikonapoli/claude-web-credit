"""Stats bar rendering for various entity stats."""

from typing import Tuple

import tcod.console


class StatsBarRenderer:
    """Renders stat bars (health, mana, etc.) for display."""

    def __init__(self, bar_width: int = 10):
        """Initialize stats bar renderer.

        Args:
            bar_width: Width of the stat bar in characters
        """
        self.bar_width = bar_width
        self.empty_char = "░"  # Light shade for empty part
        self.filled_char = "█"  # Full block for filled part

    def calculate_fill_percentage(self, current: int, maximum: int) -> float:
        """Calculate what percentage of the bar should be filled.

        Args:
            current: Current value
            maximum: Maximum value

        Returns:
            Fill percentage as a float between 0.0 and 1.0
        """
        if maximum <= 0:
            return 0.0
        return max(0.0, min(1.0, current / maximum))

    def get_health_color(self, fill_percentage: float) -> Tuple[int, int, int]:
        """Get the color for a health bar based on fill percentage.

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

    def get_mana_color(self, fill_percentage: float) -> Tuple[int, int, int]:
        """Get the color for a mana bar based on fill percentage.

        Args:
            fill_percentage: Mana percentage (0.0 to 1.0)

        Returns:
            RGB color tuple
        """
        if fill_percentage >= 0.6:
            return (100, 150, 255)  # Bright blue for high mana
        elif fill_percentage >= 0.25:
            return (70, 100, 200)  # Medium blue for medium mana
        else:
            return (50, 70, 150)  # Dark blue for low mana

    def render_bar(
        self,
        console: tcod.console.Console,
        x: int,
        y: int,
        current: int,
        maximum: int,
        color: Tuple[int, int, int],
        label: str = "",
    ) -> None:
        """Render a stat bar at the specified position.

        Args:
            console: Console to render to
            x: X position (left edge of bar)
            y: Y position
            current: Current value
            maximum: Maximum value
            color: RGB color for filled portion
            label: Optional label to show before the bar
        """
        # Render label if provided
        if label:
            console.print(x, y, label, fg=(255, 255, 255))
            x += len(label) + 1  # Move bar position after label

        fill_percentage = self.calculate_fill_percentage(current, maximum)

        # Calculate how many characters should be filled
        filled_width = int(fill_percentage * self.bar_width)

        # Render filled portion
        for i in range(filled_width):
            console.print(x + i, y, self.filled_char, fg=color)

        # Render empty portion
        empty_color = (100, 100, 100)  # Dark gray
        for i in range(filled_width, self.bar_width):
            console.print(x + i, y, self.empty_char, fg=empty_color)

        # Render numeric value at end
        value_text = f" {current}/{maximum}"
        console.print(x + self.bar_width, y, value_text, fg=(200, 200, 200))

    def render_health_bar(
        self,
        console: tcod.console.Console,
        x: int,
        y: int,
        hp: int,
        max_hp: int,
        show_label: bool = True,
    ) -> None:
        """Render a health bar.

        Args:
            console: Console to render to
            x: X position
            y: Y position
            hp: Current hit points
            max_hp: Maximum hit points
            show_label: Whether to show "HP:" label
        """
        fill_percentage = self.calculate_fill_percentage(hp, max_hp)
        color = self.get_health_color(fill_percentage)
        label = "HP:" if show_label else ""
        self.render_bar(console, x, y, hp, max_hp, color, label)

    def render_mana_bar(
        self,
        console: tcod.console.Console,
        x: int,
        y: int,
        mp: int,
        max_mp: int,
        show_label: bool = True,
    ) -> None:
        """Render a mana bar.

        Args:
            console: Console to render to
            x: X position
            y: Y position
            mp: Current mana points
            max_mp: Maximum mana points
            show_label: Whether to show "MP:" label
        """
        fill_percentage = self.calculate_fill_percentage(mp, max_mp)
        color = self.get_mana_color(fill_percentage)
        label = "MP:" if show_label else ""
        self.render_bar(console, x, y, mp, max_mp, color, label)
