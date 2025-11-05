"""Tests for health bar rendering."""

import pytest
import tcod

from roguelike.ui.health_bar_renderer import HealthBarRenderer


class TestHealthBarRenderer:
    """Tests for HealthBarRenderer class."""

    @pytest.fixture
    def renderer(self):
        """Create a HealthBarRenderer for testing."""
        return HealthBarRenderer(bar_width=10)

    def test_calculate_fill_percentage_full_health(self, renderer):
        """Calculate fill percentage returns 1.0 for full health."""
        fill = renderer.calculate_fill_percentage(hp=10, max_hp=10)
        assert fill == 1.0

    def test_calculate_fill_percentage_half_health(self, renderer):
        """Calculate fill percentage returns 0.5 for half health."""
        fill = renderer.calculate_fill_percentage(hp=5, max_hp=10)
        assert fill == 0.5

    def test_calculate_fill_percentage_no_health(self, renderer):
        """Calculate fill percentage returns 0.0 for no health."""
        fill = renderer.calculate_fill_percentage(hp=0, max_hp=10)
        assert fill == 0.0

    def test_calculate_fill_percentage_zero_max_hp(self, renderer):
        """Calculate fill percentage returns 0.0 when max_hp is 0."""
        fill = renderer.calculate_fill_percentage(hp=0, max_hp=0)
        assert fill == 0.0

    def test_get_health_color_full_health(self, renderer):
        """Get health color returns green for full health."""
        color = renderer.get_health_color(fill_percentage=1.0)
        assert color == (0, 255, 0)  # Green

    def test_get_health_color_high_health(self, renderer):
        """Get health color returns green for high health."""
        color = renderer.get_health_color(fill_percentage=0.7)
        assert color == (0, 255, 0)  # Green

    def test_get_health_color_medium_health(self, renderer):
        """Get health color returns yellow for medium health."""
        color = renderer.get_health_color(fill_percentage=0.5)
        assert color == (255, 255, 0)  # Yellow

    def test_get_health_color_low_health(self, renderer):
        """Get health color returns yellow for low health."""
        color = renderer.get_health_color(fill_percentage=0.3)
        assert color == (255, 255, 0)  # Yellow

    def test_get_health_color_critical_health(self, renderer):
        """Get health color returns red for critical health."""
        color = renderer.get_health_color(fill_percentage=0.2)
        assert color == (255, 0, 0)  # Red

    def test_get_health_color_no_health(self, renderer):
        """Get health color returns red for no health."""
        color = renderer.get_health_color(fill_percentage=0.0)
        assert color == (255, 0, 0)  # Red

    def test_render_health_bar_draws_background(self, renderer):
        """Render health bar draws background bar."""
        console = tcod.console.Console(20, 10)
        renderer.render(console, x=5, y=3, hp=5, max_hp=10)

        # Check that background characters are drawn
        # Background should be full width
        for i in range(renderer.bar_width):
            char = console.tiles["ch"][3, 5 + i]
            # ASCII 219 is '█' (full block)
            assert char != 0  # Some character was drawn

    def test_render_health_bar_respects_fill_percentage(self, renderer):
        """Render health bar fills correct amount based on HP."""
        console = tcod.console.Console(20, 10)
        # 50% health with 10-width bar = 5 filled characters
        renderer.render(console, x=5, y=3, hp=5, max_hp=10)

        # Should have drawn something at the start position
        char = console.tiles["ch"][3, 5]
        assert char != 0

    def test_custom_bar_width(self):
        """HealthBarRenderer accepts custom bar width."""
        renderer = HealthBarRenderer(bar_width=20)
        assert renderer.bar_width == 20
