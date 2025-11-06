# Targeted Confusion Scrolls - Implementation Summary

## Overview
This document describes the implementation of a targeting system for the roguelike game, specifically for targeted confusion scrolls. The system is fully implemented and tested, with 21 new tests added (all passing).

## What Has Been Implemented

### 1. TargetingSystem (`src/roguelike/systems/targeting.py`)
A complete targeting system for selecting enemies at range:
- **Range-based filtering**: Filters targets by Manhattan distance from origin
- **Dead target filtering**: Automatically excludes dead enemies
- **Cursor movement**: Move cursor manually with directional keys
- **Target cycling**: Tab/Shift+Tab to cycle through valid targets
- **Target selection**: Enter to select, Escape to cancel

**Tests**: 14 comprehensive tests in `tests/test_targeting.py`
- Range filtering
- Dead target filtering
- Cursor movement and positioning
- Target cycling (forward/backward with wraparound)
- Selection and cancellation

### 2. Input Handling (`src/roguelike/ui/input_handler.py`)
Extended the input handler to support targeting mode:
- **New Actions**:
  - `TARGETING_SELECT` - Confirm target selection (Enter/Return)
  - `TARGETING_CANCEL` - Cancel targeting (Escape)
  - `TARGETING_CYCLE_NEXT` - Next target (Tab)
  - `TARGETING_CYCLE_PREV` - Previous target (Shift+Tab)
- **Targeting Mode**: `set_targeting_mode(bool)` switches between normal and targeting input modes
- **Separate key handlers**: `_handle_targeting_keys()` processes input differently in targeting mode

### 3. UI Rendering (`src/roguelike/ui/renderer.py`)
Added targeting cursor visualization:
- **`render_targeting_cursor(position, target_name)`**: Renders a yellow "X" cursor with dark red background
- **Target name display**: Shows the name of the entity at cursor position above the cursor

### 4. Item Targeting Support (`src/roguelike/entities/item.py`)
Added targeting requirement detection:
- **`requires_targeting()`** method on Item class
- Returns `True` for:
  - `SCROLL_CONFUSION`
  - `SCROLL_FIREBALL` (for future implementation)
  - `SCROLL_LIGHTNING` (for future implementation)

### 5. ItemSystem Updates (`src/roguelike/systems/item_system.py`)
Updated to support targeted items:
- **`use_item(..., target=None)`**: Added optional target parameter
- **Targeted scroll methods**: Updated `_apply_confusion()`, `_apply_fireball()`, `_apply_lightning()` to accept target
- **Validation**: Confusion scroll now requires a living target, fails gracefully if target is None or dead

**Tests**: 7 comprehensive tests in `tests/test_targeted_items.py`
- Item targeting requirement detection
- Confusion scroll application to target
- Failure cases (no target, dead target)
- Correct effect duration
- Multiple target usage

## Integration Status

### ✅ Fully Implemented and Tested
- TargetingSystem with all core functionality
- Input handling for targeting actions
- UI rendering for targeting cursor
- Item targeting logic
- ItemSystem support for targeted items
- Comprehensive test coverage (21 new tests, all passing)
- Full test suite passes (749 tests total)

### ⏳ Pending Integration
To actually use targeted confusion scrolls in-game, the following integration is needed:

#### Option 1: Simple Test Integration
Add a test key binding to GameEngine that:
1. Checks if player has a confusion scroll in inventory
2. Starts targeting mode via TargetingSystem
3. Enables targeting input mode in InputHandler
4. Renders targeting cursor
5. On target selection, uses the scroll with the selected target

#### Option 2: Full Inventory UI Integration
Create a complete inventory UI system that:
1. Shows inventory when 'i' is pressed
2. Allows item selection
3. For items that `requires_targeting()`, enters targeting mode
4. After target selection, uses item with target
5. For non-targeted items, uses immediately

## Usage Example (Once Integrated)

```python
# In GameEngine or inventory handler:

# When player selects confusion scroll from inventory:
if item.requires_targeting():
    # Get all living monsters in FOV
    monsters = [e for e in entities if isinstance(e, Monster) and e.is_alive]

    # Start targeting
    max_range = 10  # Or item-specific range
    if targeting_system.start_targeting(player.position, max_range, monsters):
        input_handler.set_targeting_mode(True)

        # Game loop enters targeting mode...
        # Render targeting cursor each frame
        if targeting_system.is_active:
            cursor_pos = targeting_system.get_cursor_position()
            target = targeting_system.get_current_target()
            target_name = target.name if target else None
            renderer.render_targeting_cursor(cursor_pos, target_name)

        # Handle targeting input...
        if action == Action.TARGETING_SELECT:
            target = targeting_system.select_target()
            if target:
                item_system.use_item(item, player, player.inventory, target=target)
                input_handler.set_targeting_mode(False)

        elif action == Action.TARGETING_CANCEL:
            targeting_system.cancel_targeting()
            input_handler.set_targeting_mode(False)

        elif action == Action.TARGETING_CYCLE_NEXT:
            targeting_system.cycle_target(1)

        elif action == Action.TARGETING_CYCLE_PREV:
            targeting_system.cycle_target(-1)

        elif action in movement_actions:
            # Move cursor manually
            dx, dy = get_direction(action)
            targeting_system.move_cursor(dx, dy)
```

## Architecture Decisions

### Why This Design?
1. **Decoupled systems**: TargetingSystem is independent of game engine, testable in isolation
2. **Event-driven**: Uses existing EventBus for consistency
3. **Extensible**: Easy to add more targeted items (fireball, lightning)
4. **Flexible**: Supports both cursor movement and target cycling
5. **Safe**: Validates targets (alive, in range) at multiple levels

### Future Enhancements
- **AoE targeting**: For fireball (target location, affect radius)
- **Beam targeting**: For lightning (show line from player to target)
- **Range indicators**: Visual feedback for max range
- **Target info panel**: Show target HP, status effects
- **Smart targeting**: Auto-target nearest/weakest enemy

## Testing

### Run Targeting Tests
```bash
uv run pytest tests/test_targeting.py -v
uv run pytest tests/test_targeted_items.py -v
```

### Run All Tests
```bash
uv run pytest tests/ -v
```

All 749 tests pass, including 21 new tests for targeting functionality.

## Files Modified/Created

### New Files
- `src/roguelike/systems/targeting.py` - TargetingSystem implementation
- `tests/test_targeting.py` - TargetingSystem tests (14 tests)
- `tests/test_targeted_items.py` - Targeted item tests (7 tests)
- `TARGETING_IMPLEMENTATION.md` - This document

### Modified Files
- `src/roguelike/ui/input_handler.py` - Added targeting actions and mode
- `src/roguelike/ui/renderer.py` - Added targeting cursor rendering
- `src/roguelike/entities/item.py` - Added requires_targeting() method
- `src/roguelike/systems/item_system.py` - Added target parameter to use_item()

## Important: UseItemCommand Limitation

**UseItemCommand does NOT support targeted items.** The command pattern is designed for immediate, synchronous execution, which doesn't fit the targeting workflow (select item → enter targeting mode → select target → use item).

**Current behavior:**
- `UseItemCommand` checks `item.requires_targeting()`
- If `True`, returns `success=False` without consuming turn or item
- Item remains in inventory
- Non-targeted items work normally

**For inventory UI implementation:**
When implementing inventory UI, check if an item requires targeting before creating a UseItemCommand:

```python
if item.requires_targeting():
    # Enter targeting mode, store item reference
    # When target selected, use: item_system.use_item(item, player, inventory, target=target)
else:
    # Use normal UseItemCommand
    cmd = UseItemCommand(player, item_index, item_system)
    result = cmd.execute()
```

## Commits

1. **Add TargetingSystem with comprehensive tests** - Core targeting logic
2. **Add targeting mode input handling** - Input processing for targeting
3. **Add targeting cursor rendering to Renderer** - Visual feedback
4. **Add targeted item support for confusion scrolls** - Item system integration
5. **Add test key binding for confusion scroll targeting** - Game integration with 'C' key
6. **Add comprehensive targeting implementation documentation** - Usage guide
7. **Add comprehensive testing guide for targeting system** - Manual testing guide
8. **Fix turn consumption bug in targeting system** - Enemies act after item use
9. **Prevent UseItemCommand from using targeted items** - Graceful failure for targeted items

## Integration Status

### ✅ Complete
- Core targeting system with full test coverage
- Input handling for targeting mode
- UI rendering with targeting cursor
- Item targeting support (confusion, fireball, lightning)
- Turn consumption properly integrated
- UseItemCommand protections for targeted items
- Test key binding ('C') for demonstration
- **751 tests passing** (21 targeting-specific tests)

### ⏳ Pending
- Full inventory UI with targeting integration
- Visual range indicators
- AoE targeting for fireball
- Beam targeting for lightning

The core system is complete, tested, and ready to use via the 'C' test key!
