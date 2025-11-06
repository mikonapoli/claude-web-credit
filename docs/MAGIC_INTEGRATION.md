# Magic System Integration

## Overview

The magic system has been fully integrated into the game! Players can now cast spells, manage mana, and use magical abilities.

## What Was Integrated

### 1. Player Magic Capabilities
- **ManaComponent**: Player starts with 50 max MP and regenerates 2 MP per turn
- **SpellComponent**: Player starts knowing two spells:
  - Magic Missile (5 MP) - Targeted damage spell
  - Heal (8 MP) - Self-targeted healing spell

Location: `src/roguelike/entities/player.py:28-29`

### 2. Magic System Initialization
- **MagicSystem**: Initialized in GameEngine
- **SpellLoader**: Loads spells from `src/roguelike/data/spells.json`
- **Spell Effects**: All 7 spells have registered effects:
  - Damage spells: magic_missile, fireball, lightning_bolt, frost_nova
  - Healing spell: heal
  - Buff spells: shield, strength

Location: `src/roguelike/engine/game_engine.py:72, 114-137`

### 3. Mana Regeneration
- Player regenerates mana after every turn that consumes an action
- Mana changes emit events for UI updates

Location: `src/roguelike/systems/turn_manager.py:192-194`

### 4. Event Subscriptions
- **SpellCastEvent**: Shows spell name, mana cost, and effect message
- **ManaChangedEvent**: Tracks mana changes (silent by default)

Location: `src/roguelike/engine/game_engine.py:183-195`

### 5. Key Bindings
- **Z key**: Cast Magic Missile (targeted)
- **X key**: Cast Heal (self-targeted)

Location: `src/roguelike/ui/input_handler.py:103-106`

### 6. Spell Casting System
- Self-targeted spells cast immediately (Heal)
- Enemy-targeted spells enter targeting mode (Magic Missile)
- Uses existing targeting system for selecting targets
- Validates mana availability before casting
- Consumes turn after successful cast
- Awards XP for kills from spell damage

Location: `src/roguelike/engine/game_engine.py:230-283, 363-410`

### 7. UI Updates
- **Mana Bar**: Displays current/max MP in cyan below health
- **Spell List**: Shows known spells with key bindings and mana costs
- Displayed in top-right corner of screen

Location: `src/roguelike/ui/renderer.py:274-289`

## How to Play

### Casting Spells

1. **Heal (X key)**:
   - Press X to cast Heal
   - Restores 15 HP
   - Costs 8 MP
   - Instant cast (no targeting needed)

2. **Magic Missile (Z key)**:
   - Press Z to start targeting
   - Use arrow keys or hjkl to move cursor
   - Press Tab to cycle through visible monsters
   - Press Enter to cast at target
   - Press Escape to cancel
   - Deals 10 damage
   - Costs 5 MP

### Mana Management

- **Starting Mana**: 50 MP
- **Regeneration**: 2 MP per turn
- **Cost Examples**:
  - Magic Missile: 5 MP (can cast 10 times from full)
  - Heal: 8 MP (can cast 6 times from full)
  - Fireball: 15 MP (can cast 3 times from full)

### Strategy Tips

- Heal costs more than Magic Missile - use it wisely!
- You regenerate 2 MP per turn, so you can sustain 1 Magic Missile every 3 turns
- Healing is instant but expensive - consider if fighting or fleeing is better
- Mana regenerates even during combat, so kiting enemies can restore your resources

## Available Spells (Not Yet Learned)

The following spells are defined but not yet given to the player:

### Damage Spells
- **Fireball** (15 MP): Area-of-effect fire damage (25 power, radius 2)
- **Lightning Bolt** (10 MP): Beam attack (18 power, range 6)
- **Frost Nova** (12 MP): Area burst around caster (15 power, radius 3)

### Buff Spells
- **Magic Shield** (6 MP): Increase defense by 3
- **Strength** (7 MP): Increase power by 4

Note: Buff spells currently increase stats permanently. A future enhancement could add duration-based buffs.

## Future Enhancements

Potential additions:

1. **Spell Scrolls**: Convert magic scrolls to use the magic system
2. **Learning Spells**: Find spellbooks to learn new spells
3. **Spell Levels**: Scale spell power with caster level
4. **Cooldowns**: Add per-spell cooldown timers
5. **AOE Targeting**: Implement area-of-effect targeting for Fireball/Frost Nova
6. **Beam Targeting**: Implement line-of-sight targeting for Lightning Bolt
7. **Duration Buffs**: Make buff spells temporary with turn-based duration
8. **Mana Potions**: Add items that restore mana
9. **Spell Schools Mastery**: Bonuses for specializing in one school
10. **Monster Spells**: Allow monsters to cast spells

## Testing

All existing tests pass (756 tests):
```bash
uv run pytest tests/ -q
```

The magic system has 74 tests of its own in:
- `tests/test_mana.py`
- `tests/test_spell.py`
- `tests/test_spell_component.py`
- `tests/test_spell_effects.py`
- `tests/test_magic_system.py`
- `tests/test_spell_loader.py`

## Architecture Notes

The integration follows the project's coding guidelines:

- **Decoupled**: Magic system uses event bus, not direct calls
- **Component-based**: ManaComponent and SpellComponent compose into Player
- **Data-driven**: Spells loaded from JSON
- **Event-driven**: Spell casting emits events for game responses
- **Single Responsibility**: Each component has one clear purpose
- **Tested**: All 756 tests pass after integration

## Files Modified

1. `src/roguelike/entities/player.py` - Added mana and spells components
2. `src/roguelike/engine/game_engine.py` - Initialized magic system, spell loading, event handling, spell casting
3. `src/roguelike/systems/turn_manager.py` - Added mana regeneration
4. `src/roguelike/ui/input_handler.py` - Added spell casting key bindings
5. `src/roguelike/ui/renderer.py` - Added mana bar and spell list rendering

## Documentation References

- Magic System Design: `docs/MAGIC_SYSTEM.md`
- Development Guidelines: `DEVELOPMENT.md`
- Spell Data: `src/roguelike/data/spells.json`
