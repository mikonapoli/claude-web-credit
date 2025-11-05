"""Tests for ManaComponent."""

import pytest
from roguelike.components.mana import ManaComponent


def test_mana_component_initializes_with_max_mp():
    """ManaComponent starts at max mana."""
    mana = ManaComponent(max_mp=100)
    assert mana.mp == 100


def test_mana_component_respects_max_mp():
    """Mana cannot exceed max_mp."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 150
    assert mana.mp == 100


def test_mana_component_cannot_go_below_zero():
    """Mana cannot go below zero."""
    mana = ManaComponent(max_mp=100)
    mana.mp = -10
    assert mana.mp == 0


def test_has_mana_returns_true_when_sufficient():
    """has_mana returns True when entity has enough mana."""
    mana = ManaComponent(max_mp=100)
    assert mana.has_mana(50) is True


def test_has_mana_returns_false_when_insufficient():
    """has_mana returns False when entity lacks mana."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 30
    assert mana.has_mana(50) is False


def test_has_mana_returns_true_when_exact():
    """has_mana returns True when mana equals requirement."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 50
    assert mana.has_mana(50) is True


def test_consume_mana_reduces_mp_when_sufficient():
    """consume_mana reduces MP when available."""
    mana = ManaComponent(max_mp=100)
    result = mana.consume_mana(30)
    assert result is True
    assert mana.mp == 70


def test_consume_mana_fails_when_insufficient():
    """consume_mana fails when mana insufficient."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 20
    result = mana.consume_mana(30)
    assert result is False
    assert mana.mp == 20


def test_consume_mana_succeeds_when_exact():
    """consume_mana succeeds when mana exactly matches."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 30
    result = mana.consume_mana(30)
    assert result is True
    assert mana.mp == 0


def test_restore_mana_increases_mp():
    """restore_mana increases current mana."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 50
    restored = mana.restore_mana(20)
    assert restored == 20
    assert mana.mp == 70


def test_restore_mana_caps_at_max_mp():
    """restore_mana cannot exceed max_mp."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 90
    restored = mana.restore_mana(20)
    assert restored == 10
    assert mana.mp == 100


def test_restore_mana_when_already_full():
    """restore_mana does nothing when already at max."""
    mana = ManaComponent(max_mp=100)
    restored = mana.restore_mana(20)
    assert restored == 0
    assert mana.mp == 100


def test_regenerate_restores_mana_at_regen_rate():
    """regenerate restores mana based on mp_regen_rate."""
    mana = ManaComponent(max_mp=100, mp_regen_rate=5)
    mana.mp = 50
    regenerated = mana.regenerate()
    assert regenerated == 5
    assert mana.mp == 55


def test_regenerate_respects_max_mp():
    """regenerate cannot exceed max_mp."""
    mana = ManaComponent(max_mp=100, mp_regen_rate=5)
    mana.mp = 98
    regenerated = mana.regenerate()
    assert regenerated == 2
    assert mana.mp == 100


def test_mana_percentage_calculation():
    """mana_percentage returns correct percentage."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 75
    assert mana.mana_percentage == 0.75


def test_mana_percentage_when_empty():
    """mana_percentage returns 0 when empty."""
    mana = ManaComponent(max_mp=100)
    mana.mp = 0
    assert mana.mana_percentage == 0.0


def test_mana_percentage_when_full():
    """mana_percentage returns 1.0 when full."""
    mana = ManaComponent(max_mp=100)
    assert mana.mana_percentage == 1.0


def test_mana_percentage_with_zero_max_mp():
    """mana_percentage returns 0 when max_mp is 0."""
    mana = ManaComponent(max_mp=0)
    assert mana.mana_percentage == 0.0
