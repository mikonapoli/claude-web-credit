# Testing Guide - Targeted Confusion Scrolls

## How to Test the Targeting System

The targeting system is now integrated into the game with a test key binding. Here's how to use it:

### Starting the Game

```bash
uv run python main.py
```

### Using the Confusion Targeting System

1. **Press 'C' key** to activate confusion scroll targeting
   - If there are no visible enemies, you'll see: "No visible targets!"
   - If there are no enemies in range (10 tiles), you'll see: "No targets in range!"
   - If targeting starts successfully, you'll see: "Select a target (Tab to cycle, Enter to select, Escape to cancel)"

2. **While in targeting mode:**
   - **Arrow keys / HJKL (vi keys)**: Move the targeting cursor manually
   - **Tab**: Cycle to the next target
   - **Shift+Tab**: Cycle to the previous target
   - **Enter**: Select the current target and apply confusion
   - **Escape**: Cancel targeting

3. **Visual Feedback:**
   - Yellow "X" cursor shows where you're targeting
   - Target name appears above the cursor
   - Cursor is highlighted with a dark red background

4. **After Selecting a Target:**
   - If successful: "You confuse the {monster name} for 10 turns!"
   - If failed: "Failed to confuse target!"
   - The confused monster will wander randomly for 10 turns

### What to Observe

#### Confused Monster Behavior
Once a monster is confused:
- It will move randomly in any direction instead of chasing the player
- It won't attack the player even if adjacent
- The confusion lasts for 10 turns
- You'll see messages like: "{Monster} is affected by Confusion for 10 turns!"
- When it expires: "{Monster}'s Confusion effect has worn off."

#### Targeting System Features to Test

1. **Range Limiting**: Try moving away from monsters and pressing 'C' - distant monsters (>10 tiles) won't be targetable

2. **Visibility**: Monsters outside your field of view won't be targetable

3. **Cursor Movement**:
   - Move cursor with arrow keys
   - It should stay within the max range (10 tiles from player)
   - Moving beyond range should be prevented

4. **Target Cycling**:
   - If multiple monsters are visible, Tab should cycle through them
   - Shift+Tab should cycle backwards
   - Cycling should wrap around (last → first, first → last)

5. **Cancellation**:
   - Press Escape to cancel targeting
   - Message: "Targeting cancelled."
   - Game returns to normal mode

### Testing Scenarios

#### Scenario 1: Single Monster
1. Wait for a monster to appear in your FOV
2. Press 'C' to start targeting
3. The cursor should automatically appear on the monster
4. Press Enter to select
5. Watch the monster wander randomly

#### Scenario 2: Multiple Monsters
1. Find 2-3 monsters in your FOV
2. Press 'C' to start targeting
3. Press Tab to cycle through targets
4. Try Shift+Tab to go backwards
5. Select one with Enter

#### Scenario 3: Manual Cursor Movement
1. Start targeting (C key)
2. Use arrow keys to move cursor away from monsters
3. Move it back to a monster
4. Press Enter to select

#### Scenario 4: Cancel Targeting
1. Start targeting (C key)
2. Press Escape
3. Verify you're back in normal mode (can move player)

#### Scenario 5: Range Limitation
1. Find a monster
2. Move very far away (>10 tiles)
3. Press 'C'
4. Should see "No targets in range!"

### Known Limitations

This is a test implementation with the following limitations:

1. **No actual scroll consumption**: The confusion effect is applied without requiring a scroll in inventory
2. **No range indicator**: There's no visual feedback showing the 10-tile range limit
3. **Single use per keypress**: Each 'C' press applies one confusion effect
4. **No cost**: Unlimited uses for testing purposes

### Debugging

If something doesn't work:

1. **Check the message log** at the bottom of the screen for error messages
2. **Verify monsters are visible**: Move around to get monsters in your FOV
3. **Check range**: Make sure you're within 10 tiles of targets
4. **Console output**: Run from terminal to see any Python errors

### Test Checklist

- [ ] Press 'C' with no monsters visible
- [ ] Press 'C' with 1 monster visible
- [ ] Press 'C' with multiple monsters visible
- [ ] Move cursor with arrow keys
- [ ] Cycle targets with Tab
- [ ] Cycle backwards with Shift+Tab
- [ ] Select target with Enter
- [ ] Observe confused monster behavior
- [ ] Cancel targeting with Escape
- [ ] Try targeting from maximum range (10 tiles)
- [ ] Try targeting from beyond maximum range

### Success Criteria

✅ The targeting system is working correctly if:
- Cursor appears when 'C' is pressed with valid targets
- Cursor can be moved and cycled between targets
- Target name appears above cursor
- Selecting a target applies confusion effect
- Confused monsters wander randomly
- Cancellation returns to normal game mode
- All 749 tests still pass

## Technical Details

### Key Bindings
- `C`: Start confusion targeting (test key)
- `Tab`: Next target (in targeting mode)
- `Shift+Tab`: Previous target (in targeting mode)
- `Enter`: Select target (in targeting mode)
- `Escape`: Cancel targeting (in targeting mode)
- `Arrow keys / HJKL`: Move cursor (in targeting mode)

### Files Modified
- `src/roguelike/ui/input_handler.py` - Added TEST_CONFUSION action
- `src/roguelike/engine/game_engine.py` - Integrated targeting system

### Test Results
```bash
$ uv run pytest tests/ -q
749 passed, 3 warnings in 2.42s
```

All tests pass after integration! ✅
