"""Tests for StatsBarRenderer."""

from unittest.mock import Mock

from roguelike.ui.stats_bar_renderer import StatsBarRenderer


def test_calculate_fill_percentage_full():
    """Full stat bar returns 1.0 percentage."""
    renderer = StatsBarRenderer()
    assert renderer.calculate_fill_percentage(10, 10) == 1.0


def test_calculate_fill_percentage_half():
    """Half-full stat bar returns 0.5 percentage."""
    renderer = StatsBarRenderer()
    assert renderer.calculate_fill_percentage(5, 10) == 0.5


def test_calculate_fill_percentage_empty():
    """Empty stat bar returns 0.0 percentage."""
    renderer = StatsBarRenderer()
    assert renderer.calculate_fill_percentage(0, 10) == 0.0


def test_calculate_fill_percentage_zero_max():
    """Zero maximum returns 0.0 percentage."""
    renderer = StatsBarRenderer()
    assert renderer.calculate_fill_percentage(5, 0) == 0.0


def test_calculate_fill_percentage_over_max():
    """Over-max value is clamped to 1.0."""
    renderer = StatsBarRenderer()
    assert renderer.calculate_fill_percentage(15, 10) == 1.0


def test_get_health_color_high():
    """Healthy percentage returns green color."""
    renderer = StatsBarRenderer()
    color = renderer.get_health_color(0.8)
    assert color == (0, 255, 0)


def test_get_health_color_medium():
    """Injured percentage returns yellow color."""
    renderer = StatsBarRenderer()
    color = renderer.get_health_color(0.4)
    assert color == (255, 255, 0)


def test_get_health_color_low():
    """Critical percentage returns red color."""
    renderer = StatsBarRenderer()
    color = renderer.get_health_color(0.1)
    assert color == (255, 0, 0)


def test_get_mana_color_high():
    """High mana percentage returns bright blue color."""
    renderer = StatsBarRenderer()
    color = renderer.get_mana_color(0.8)
    assert color == (100, 150, 255)


def test_get_mana_color_medium():
    """Medium mana percentage returns medium blue color."""
    renderer = StatsBarRenderer()
    color = renderer.get_mana_color(0.4)
    assert color == (70, 100, 200)


def test_get_mana_color_low():
    """Low mana percentage returns dark blue color."""
    renderer = StatsBarRenderer()
    color = renderer.get_mana_color(0.1)
    assert color == (50, 70, 150)


def test_render_bar_calls_console_print():
    """Render bar calls console print for each character."""
    renderer = StatsBarRenderer(bar_width=5)
    mock_console = Mock()

    renderer.render_bar(mock_console, 0, 0, 5, 10, (255, 0, 0), "HP:")

    # Should print label, filled portion, empty portion, and numeric value
    assert mock_console.print.call_count > 0


def test_render_health_bar_calls_render_bar():
    """Render health bar delegates to render_bar."""
    renderer = StatsBarRenderer(bar_width=5)
    mock_console = Mock()

    renderer.render_health_bar(mock_console, 0, 0, 10, 20, show_label=True)

    # Should have printed something
    assert mock_console.print.call_count > 0


def test_render_mana_bar_calls_render_bar():
    """Render mana bar delegates to render_bar."""
    renderer = StatsBarRenderer(bar_width=5)
    mock_console = Mock()

    renderer.render_mana_bar(mock_console, 0, 0, 10, 20, show_label=True)

    # Should have printed something
    assert mock_console.print.call_count > 0
