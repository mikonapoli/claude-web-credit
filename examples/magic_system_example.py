"""Example of how to integrate and use the magic system.

This file demonstrates how to:
1. Set up the magic system
2. Give entities mana and spells
3. Register spell effects
4. Cast spells
5. Handle magic events
"""

from roguelike.components.mana import ManaComponent
from roguelike.components.spells import SpellComponent
from roguelike.data.spell_loader import SpellLoader
from roguelike.engine.events import EventBus, ManaChangedEvent, SpellCastEvent
from roguelike.entities.actor import Actor
from roguelike.magic.effects import DamageEffect, HealEffect, BuffEffect
from roguelike.systems.magic_system import MagicSystem
from roguelike.utils.position import Position


def setup_magic_system(event_bus: EventBus) -> tuple[MagicSystem, SpellLoader]:
    """Set up the magic system with spell effects.

    Args:
        event_bus: Event bus for magic events

    Returns:
        Tuple of (magic_system, spell_loader)
    """
    # Create magic system
    magic_system = MagicSystem(event_bus)

    # Load spells from data file
    spell_loader = SpellLoader()

    # Register spell effects for each spell type
    # Evocation spells (damage)
    magic_system.register_spell_effect("magic_missile", DamageEffect())
    magic_system.register_spell_effect("fireball", DamageEffect())
    magic_system.register_spell_effect("lightning_bolt", DamageEffect())
    magic_system.register_spell_effect("frost_nova", DamageEffect())

    # Transmutation spells
    magic_system.register_spell_effect("heal", HealEffect())
    magic_system.register_spell_effect("shield", BuffEffect(buff_amount=3))  # Defense buff
    magic_system.register_spell_effect("strength", BuffEffect(buff_amount=4))  # Power buff

    return magic_system, spell_loader


def create_mage_player() -> tuple[Actor, ManaComponent, SpellComponent]:
    """Create a player character with magic abilities.

    Returns:
        Tuple of (player, mana_component, spell_component)
    """
    # Create player actor
    player = Actor(
        position=Position(5, 5),
        char="@",
        name="Player Mage",
        max_hp=50,
        defense=2,
        power=5,
    )

    # Add mana component
    mana_component = ManaComponent(max_mp=50, mp_regen_rate=2)

    # Add spell component
    spell_component = SpellComponent()

    return player, mana_component, spell_component


def give_starting_spells(
    spell_component: SpellComponent, spell_loader: SpellLoader
) -> None:
    """Give player starting spells.

    Args:
        spell_component: Player's spell component
        spell_loader: Spell loader to get spells from
    """
    # Learn starting spells
    starting_spell_ids = ["magic_missile", "heal"]

    for spell_id in starting_spell_ids:
        spell = spell_loader.get_spell(spell_id)
        if spell:
            spell_component.learn_spell(spell)
            print(f"Learned spell: {spell.name}")


def setup_magic_event_logging(event_bus: EventBus) -> None:
    """Set up event listeners to log magic events.

    Args:
        event_bus: Event bus to subscribe to
    """

    def on_spell_cast(event: SpellCastEvent) -> None:
        """Handle spell cast events."""
        print(f"\n[SPELL CAST] {event.caster_name} cast {event.spell_name}!")
        print(f"  Mana cost: {event.mana_cost}")
        print(f"  {event.effect_message}")

    def on_mana_changed(event: ManaChangedEvent) -> None:
        """Handle mana changed events."""
        change = event.new_mp - event.old_mp
        sign = "+" if change > 0 else ""
        print(
            f"[MANA] {event.entity_name}: {event.old_mp} → {event.new_mp} "
            f"({sign}{change}) / {event.max_mp}"
        )

    # Subscribe to events
    event_bus.subscribe("spell_cast", on_spell_cast)
    event_bus.subscribe("mana_changed", on_mana_changed)


def example_spell_casting() -> None:
    """Example of using the magic system."""
    print("=== Magic System Example ===\n")

    # 1. Set up event bus and magic system
    event_bus = EventBus()
    magic_system, spell_loader = setup_magic_system(event_bus)
    setup_magic_event_logging(event_bus)

    # 2. Create player with magic abilities
    player, mana_component, spell_component = create_mage_player()
    give_starting_spells(spell_component, spell_loader)

    # 3. Create an enemy
    enemy = Actor(
        position=Position(8, 5),
        char="o",
        name="Orc",
        max_hp=30,
        defense=1,
        power=4,
    )

    print(f"\nPlayer HP: {player.hp}/{player.max_hp}")
    print(f"Player MP: {mana_component.mp}/{mana_component.max_mp}")
    print(f"Enemy HP: {enemy.hp}/{enemy.max_hp}\n")

    # 4. Cast Magic Missile at enemy
    print("--- Casting Magic Missile at enemy ---")
    magic_missile = spell_loader.get_spell("magic_missile")
    if magic_missile:
        result = magic_system.cast_spell(
            player, enemy, magic_missile, mana_component, spell_component
        )
        print(f"Enemy HP: {enemy.hp}/{enemy.max_hp}")

    # 5. Take damage
    print("\n--- Player takes damage ---")
    player.take_damage(20)
    print(f"Player HP: {player.hp}/{player.max_hp}")

    # 6. Cast Heal on self
    print("\n--- Casting Heal on self ---")
    heal = spell_loader.get_spell("heal")
    if heal:
        result = magic_system.cast_spell(
            player, player, heal, mana_component, spell_component
        )
        print(f"Player HP: {player.hp}/{player.max_hp}")

    # 7. Mana regeneration
    print("\n--- Resting to regenerate mana ---")
    for turn in range(3):
        magic_system.regenerate_mana(player.name, mana_component)

    # 8. Learn a new spell
    print("\n--- Learning new spell ---")
    fireball = spell_loader.get_spell("fireball")
    if fireball:
        spell_component.learn_spell(fireball)
        print(f"Learned: {fireball.name}")
        print(f"  Mana cost: {fireball.mana_cost}")
        print(f"  Power: {fireball.power}")
        print(f"  School: {fireball.school.name}")

    # 9. Show all known spells
    print("\n--- Known Spells ---")
    for spell in spell_component.spells:
        print(f"  {spell.name} ({spell.school.name}) - {spell.mana_cost} MP")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    example_spell_casting()
