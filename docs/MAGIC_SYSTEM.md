# Magic System

A complete, modular magic system for the roguelike game, inspired by DCSS (Dungeon Crawl Stone Soup).

## Overview

The magic system is built on the following principles:

- **Mana-based**: Spells consume mana (MP), which regenerates over time
- **Spell schools**: Spells belong to schools (Evocation, Conjuration, Transmutation)
- **Component-based**: Uses `ManaComponent` and `SpellComponent` for entity composition
- **Data-driven**: Spells defined in JSON, easy to add new spells
- **Event-driven**: Magic actions emit events for decoupled game responses
- **Modular effects**: Spell effects are composable and reusable

## Architecture

### Core Components

#### 1. ManaComponent
Manages an entity's mana pool.

```python
from roguelike.components.mana import ManaComponent

# Create mana component
mana = ManaComponent(max_mp=50, mp_regen_rate=2)

# Check and consume mana
if mana.has_mana(10):
    mana.consume_mana(10)

# Restore mana
mana.restore_mana(5)

# Regenerate per turn
mana.regenerate()
```

#### 2. SpellComponent
Manages an entity's known spells.

```python
from roguelike.components.spells import SpellComponent
from roguelike.magic.spell import Spell

spell_component = SpellComponent()

# Learn spells
spell_component.learn_spell(magic_missile)

# Check knowledge
if spell_component.knows_spell("magic_missile"):
    spell = spell_component.get_spell("magic_missile")

# Get spells by school
evocation_spells = spell_component.get_spells_by_school(SpellSchool.EVOCATION)
```

#### 3. Spell Data Model
Defines spell properties.

```python
from roguelike.magic.spell import Spell, SpellSchool, TargetType

spell = Spell(
    id="magic_missile",
    name="Magic Missile",
    school=SpellSchool.EVOCATION,
    mana_cost=5,
    power=10,
    target_type=TargetType.SINGLE,
    range=5,
    description="A dart of magical force"
)
```

#### 4. Spell Effects
Implement what spells do when cast.

```python
from roguelike.magic.effects import DamageEffect, HealEffect, BuffEffect

# Built-in effects:
damage = DamageEffect()  # Deals damage
heal = HealEffect()      # Restores HP
buff = BuffEffect(buff_amount=3)  # Increases power
```

#### 5. MagicSystem
Coordinates spell casting.

```python
from roguelike.systems.magic_system import MagicSystem

magic_system = MagicSystem(event_bus)

# Register spell effects
magic_system.register_spell_effect("magic_missile", DamageEffect())
magic_system.register_spell_effect("heal", HealEffect())

# Cast spell
result = magic_system.cast_spell(
    caster=player,
    target=enemy,
    spell=magic_missile,
    mana_component=player_mana,
    spell_component=player_spells
)

# Regenerate mana each turn
magic_system.regenerate_mana(player.name, player_mana)
```

## Spell Schools

### Evocation
Direct damage and energy manipulation.

- **Magic Missile**: Single-target force damage
- **Fireball**: Area-of-effect fire damage
- **Lightning Bolt**: Linear beam of electricity
- **Frost Nova**: Area burst of cold

### Transmutation
Transformation and self-enhancement.

- **Heal**: Restore HP
- **Magic Shield**: Increase defense temporarily
- **Strength**: Increase power temporarily

### Conjuration
Summoning and creation (extensible for future).

## Target Types

- **SELF**: Affects only the caster
- **SINGLE**: Single target at range
- **AREA**: Area of effect with radius
- **BEAM**: Linear beam through multiple targets

## Data Files

### Spell Data Location

Spell data is packaged inside the module at `src/roguelike/data/spells.json`. This ensures spells are available when the package is installed via pip or wheel.

### Adding New Spells

Edit `src/roguelike/data/spells.json`:

```json
{
  "spells": [
    {
      "id": "new_spell",
      "name": "New Spell",
      "school": "EVOCATION",
      "mana_cost": 10,
      "power": 20,
      "target_type": "SINGLE",
      "range": 6,
      "description": "A powerful new spell"
    }
  ]
}
```

The `SpellLoader` uses `importlib.resources` to load spells from the package, so they work correctly in both development and installed environments.

Then register its effect in your game initialization:

```python
magic_system.register_spell_effect("new_spell", DamageEffect())
```

### Custom Spell Files

You can also load spells from a custom location:

```python
from pathlib import Path

# Load from custom path
loader = SpellLoader(data_path=Path("/path/to/custom_spells.json"))
```

## Events

The magic system emits events for game integration:

### SpellCastEvent
```python
def on_spell_cast(event: SpellCastEvent):
    print(f"{event.caster_name} cast {event.spell_name}!")
    print(event.effect_message)

event_bus.subscribe("spell_cast", on_spell_cast)
```

### ManaChangedEvent
```python
def on_mana_changed(event: ManaChangedEvent):
    print(f"{event.entity_name}: {event.old_mp} → {event.new_mp}")

event_bus.subscribe("mana_changed", on_mana_changed)
```

## Integration Guide

### 1. Set Up Magic System

```python
from roguelike.engine.events import EventBus
from roguelike.systems.magic_system import MagicSystem
from roguelike.data.spell_loader import SpellLoader
from roguelike.magic.effects import DamageEffect, HealEffect

# Create system
event_bus = EventBus()
magic_system = MagicSystem(event_bus)
spell_loader = SpellLoader()

# Register effects for all spells
magic_system.register_spell_effect("magic_missile", DamageEffect())
magic_system.register_spell_effect("heal", HealEffect())
# ... register others
```

### 2. Give Entity Magic Abilities

```python
from roguelike.components.mana import ManaComponent
from roguelike.components.spells import SpellComponent

# Add to player or monster
mana_component = ManaComponent(max_mp=50, mp_regen_rate=2)
spell_component = SpellComponent()

# Learn starting spells
magic_missile = spell_loader.get_spell("magic_missile")
spell_component.learn_spell(magic_missile)
```

### 3. Handle Spell Casting

```python
# In your turn handler or input handler
def cast_spell(caster, target, spell_id):
    spell = spell_component.get_spell(spell_id)
    if not spell:
        return

    result = magic_system.cast_spell(
        caster, target, spell,
        mana_component, spell_component
    )

    if result.success:
        # Handle successful cast
        if result.target_died:
            # Handle death
            pass
    else:
        # Show error message
        print(result.message)
```

### 4. Regenerate Mana Each Turn

```python
# In your turn manager
def process_turn():
    # After each action
    magic_system.regenerate_mana(entity.name, mana_component)
```

## Creating Custom Effects

Implement the `SpellEffect` protocol:

```python
from roguelike.magic.effects import SpellEffect, EffectResult
from roguelike.utils.protocols import Combatant

class CustomEffect:
    """Custom spell effect."""

    def apply(self, caster: Combatant, target: Combatant, power: int) -> EffectResult:
        # Implement effect logic
        # ...

        return EffectResult(
            success=True,
            message=f"Custom effect applied!",
            damage_dealt=0,
            healing_done=0,
            target_died=False
        )
```

Then register it:

```python
magic_system.register_spell_effect("custom_spell", CustomEffect())
```

## Testing

Run the complete test suite:

```bash
uv run pytest tests/test_mana.py -v           # Mana component tests
uv run pytest tests/test_spell.py -v          # Spell model tests
uv run pytest tests/test_spell_component.py -v # Spell component tests
uv run pytest tests/test_spell_effects.py -v  # Spell effects tests
uv run pytest tests/test_magic_system.py -v   # Magic system tests
uv run pytest tests/test_spell_loader.py -v   # Spell loader tests
```

All magic system tests: **74 tests passing**

## Example

See `examples/magic_system_example.py` for a complete working example:

```bash
uv run python examples/magic_system_example.py
```

## Future Enhancements

Potential additions to the magic system:

1. **Spell cooldowns**: Per-spell cooldown timers
2. **Spell levels**: Spells that scale with caster level
3. **Status effects**: Buffs/debuffs with duration tracking
4. **Spell combinations**: Chain spells for bonus effects
5. **Spell schools mastery**: Bonuses for focusing on one school
6. **Conjuration spells**: Summon creatures to fight for you
7. **Spell scrolls**: One-time use spell items
8. **Mana burn**: Risk-based overcasting for more power

## Design Principles

The magic system follows the project's coding guidelines:

- **Decoupled**: Systems communicate via events, not direct calls
- **Component-based**: Composition over inheritance
- **Data-driven**: Spells in JSON, not hardcoded
- **Tested**: 74 tests covering all functionality
- **Extensible**: Easy to add new spells, effects, and schools
