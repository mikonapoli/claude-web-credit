"""Tests for Actor class."""

from roguelike.entities.actor import Actor
from roguelike.utils.position import Position


def test_actor_creation():
    """Actor can be created with combat stats."""
    actor = Actor(
        position=Position(0, 0),
        char="@",
        name="Hero",
        max_hp=30,
        defense=2,
        power=5
    )
    assert actor.name == "Hero"


def test_actor_max_hp():
    """Actor stores max HP correctly."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    assert actor.max_hp == 30


def test_actor_starts_at_max_hp():
    """Actor starts with HP equal to max HP."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    assert actor.hp == 30


def test_actor_defense():
    """Actor stores defense correctly."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    assert actor.defense == 2


def test_actor_power():
    """Actor stores power correctly."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    assert actor.power == 5


def test_actor_blocks_movement():
    """Actor blocks movement by default."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    assert actor.blocks_movement


def test_actor_is_alive_at_full_hp():
    """Actor is alive when at full HP."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    assert actor.is_alive


def test_actor_take_damage():
    """Actor can take damage."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    damage_taken = actor.take_damage(10)
    assert damage_taken == 10


def test_actor_hp_after_damage():
    """Actor HP decreases after taking damage."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    actor.take_damage(10)
    assert actor.hp == 20


def test_actor_hp_cannot_go_negative():
    """Actor HP cannot go below 0."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    actor.take_damage(50)
    assert actor.hp == 0


def test_actor_dies_at_zero_hp():
    """Actor is not alive when HP reaches 0."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    actor.take_damage(30)
    assert not actor.is_alive


def test_actor_heal():
    """Actor can be healed."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    actor.take_damage(10)
    healed = actor.heal(5)
    assert healed == 5


def test_actor_hp_after_healing():
    """Actor HP increases after healing."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    actor.take_damage(10)
    actor.heal(5)
    assert actor.hp == 25


def test_actor_cannot_heal_above_max_hp():
    """Actor HP cannot exceed max HP."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    actor.heal(100)
    assert actor.hp == 30


def test_actor_healing_returns_actual_amount():
    """Heal returns actual amount healed, not exceeding max HP."""
    actor = Actor(Position(0, 0), "@", "Hero", max_hp=30, defense=2, power=5)
    actor.take_damage(5)
    healed = actor.heal(100)
    assert healed == 5
