# Development Guidelines

This document defines the development practices and standards for this roguelike project. **Follow these guidelines rigorously** when implementing new features or making changes.

## Package Management

**Use `uv` exclusively** for all dependency and virtual environment management.

```bash
# Install dependencies
uv sync

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Update dependencies
uv sync --upgrade
```

**Never use:** `pip`, `pip-tools`, `poetry`, or `pipenv` for this project.

## Code Organization and Architecture

### Extreme Attention to Decoupling

**This is the highest priority.** Code must be extremely well-organized and decoupled at all times.

**Principles:**
- **Single Responsibility**: Each class/function has exactly one reason to change
- **Things that change together**: Keep in the same module
- **Things that change independently**: Keep in separate modules
- **Composition over inheritance**: Prefer component-based design
- **Dependency Inversion**: Depend on abstractions (protocols), not concrete implementations
- **Open/Closed**: Open for extension, closed for modification

**Run refactoring cycles constantly** - don't let technical debt accumulate.

### Refactoring Frequency

Refactor **immediately** when you notice:
- A class with more than 3-4 responsibilities
- Functions longer than 30-40 lines
- Tight coupling between unrelated systems
- Duplicate code patterns
- God objects coordinating too much

**Schedule regular refactoring passes** even when nothing is obviously wrong.

### Current Architecture Patterns

This codebase uses:
1. **Event-driven architecture** - Systems communicate via events, not direct calls
2. **Component-based entities** - Composition over inheritance for entity behaviors
3. **Command pattern** - All actions are encapsulated as commands (enables undo/redo)
4. **Data-driven configuration** - Entities defined in JSON, not hardcoded
5. **System-based organization** - MovementSystem, CombatSystem, AISystem, etc.

**Maintain these patterns** when adding new features.

## Testing

### Test Everything, Test Often

- **Write tests BEFORE or DURING implementation**, never after
- **Run tests after every small change** - don't accumulate untested code
- **All tests must pass** before committing
- **Test coverage is mandatory** for all new code

### One Assertion Per Test

**Each test should have exactly ONE assertion** (or a tightly related group).

**Why:** When a test fails, you should **immediately know** what broke. No debugging required.

❌ **Bad Example:**
```python
def test_player_combat():
    """Player can attack and take damage."""
    player.attack(orc)
    assert orc.hp < orc.max_hp
    assert player.xp > 0
    orc.attack(player)
    assert player.hp < player.max_hp
```
*If this fails, which assertion failed? What broke?*

✅ **Good Example:**
```python
def test_player_attack_damages_enemy():
    """Player attack reduces enemy HP."""
    player.attack(orc)
    assert orc.hp < orc.max_hp

def test_player_attack_awards_xp():
    """Killing enemy awards XP to player."""
    player.attack(orc)  # Kill orc
    assert player.xp > 0

def test_enemy_attack_damages_player():
    """Enemy attack reduces player HP."""
    orc.attack(player)
    assert player.hp < player.max_hp
```
*Each test has one clear purpose. Failures are immediately obvious.*

### Test Organization

- Put all tests in `tests/` directory
- Name test files `test_<module>.py`
- Name test functions `test_<specific_behavior>()`
- Use descriptive docstrings explaining WHAT is tested
- Group related tests in the same file

### Running Tests

```bash
# Run all tests
.venv/bin/pytest tests/ -q

# Run specific test file
.venv/bin/pytest tests/test_combat.py -v

# Run specific test
.venv/bin/pytest tests/test_combat.py::test_player_attack_damages_enemy -v
```

## Commit Practices

### Commit Frequency

**Commit extremely often** - after every small, working change.

**Definition of "small change":**
- Added one function with tests
- Fixed one bug with regression test
- Refactored one class
- Added one component type

**Never accumulate** multiple unrelated changes in one commit.

### Commit Message Format

**Format:** `<imperative verb> <what changed>`

**Keep messages clear and succinct.** Sacrifice grammar for brevity if necessary.

✅ **Good Examples:**
```
Add HealthComponent for entities
Fix corpse blocking movement
Implement State pattern for MonsterAI
Extract AISystem, reduce GameEngine by 50 lines
Update entity factory for new component
```

❌ **Bad Examples:**
```
"Updated some files"  # Too vague
"This commit adds a new health component system that allows entities to have health and take damage, and also refactors the combat system to use it"  # Too long
"Added health component, fixed movement bug, refactored AI"  # Multiple unrelated changes
```

### Commit Message Details

If the change is complex, add details in the commit body:

```
Add Command pattern for actions

- Create Command base class with execute/undo
- Implement MoveCommand, WaitCommand, QuitCommand
- Add CommandExecutor for history management
- Support undo/redo functionality
- 14 new tests, all 199 tests passing
```

**Always include test status** in commit messages for features/fixes.

## Research Before Adding Dependencies

**Before adding ANY library:**

1. **Research thoroughly** - what options exist?
2. **Check recency** - is it actively maintained? (check GitHub commits, PyPI release dates)
3. **Check popularity** - is it widely used? (GitHub stars, downloads)
4. **Check compatibility** - does it work with Python 3.12+?
5. **Prefer modern solutions** over legacy libraries
6. **Avoid bloat** - don't add a huge library for one small feature

**Examples:**
- ✅ Use `tcod` for roguelike terminal rendering (modern, maintained, purpose-built)
- ✅ Use `pytest` for testing (industry standard, feature-rich)
- ❌ Don't use `nose` (unmaintained since 2015)
- ❌ Don't add `pandas` just to read a CSV file (use `csv` module)

## Development Workflow

### Implementing a New Feature

1. **Plan the architecture** - how does this fit with existing systems?
2. **Write tests first** - TDD approach preferred
3. **Implement in tiny increments** - one function/method at a time
4. **Run tests after each change** - ensure nothing breaks
5. **Refactor immediately** - keep code clean as you go
6. **Commit after each working increment** - don't batch commits
7. **Test the full feature** - integration testing
8. **Final refactoring pass** - improve organization and naming
9. **Push to remote** - keep remote branch up to date

### Fixing a Bug

1. **Write a failing test** that demonstrates the bug
2. **Verify the test fails** - proves you're testing the right thing
3. **Fix the bug** with minimal changes
4. **Verify the test passes** - proves the fix works
5. **Run all tests** - ensure no regressions
6. **Commit with clear message** - include "Fix" in message
7. **Push immediately** - bug fixes are high priority

### Refactoring

1. **Ensure all tests pass** before starting
2. **Make ONE refactoring at a time** - don't change everything at once
3. **Run tests after EACH refactoring** - catch breaks immediately
4. **Commit after each refactoring** - makes rollback easy if needed
5. **Update tests if interfaces change** - keep tests in sync
6. **Verify full test suite** before pushing

## Code Style

### General Guidelines

- **Type hints** on all function signatures
- **Docstrings** on all public functions/classes
- **Clear naming** - prefer verbose over cryptic
- **Keep functions short** - under 30-40 lines
- **Keep classes focused** - under 200 lines
- **No god objects** - refactor if a class does too much
- **Avoid deep nesting** - max 3-4 levels of indentation

### Imports

- Group imports: stdlib, third-party, local
- Use absolute imports: `from roguelike.systems.combat import CombatSystem`
- Avoid wildcard imports: `from module import *`

### Example of Well-Structured Code

```python
"""Combat system for handling attacks and damage."""

from roguelike.components.health import HealthComponent
from roguelike.components.combat import CombatComponent
from roguelike.engine.events import EventBus, CombatEvent


class CombatSystem:
    """Manages combat resolution and damage calculation."""

    def __init__(self, event_bus: EventBus):
        """Initialize combat system.

        Args:
            event_bus: Event bus for publishing combat events
        """
        self.event_bus = event_bus

    def resolve_attack(
        self,
        attacker: CombatComponent,
        defender: HealthComponent
    ) -> bool:
        """Resolve an attack from attacker to defender.

        Args:
            attacker: Entity attacking
            defender: Entity being attacked

        Returns:
            True if defender died from the attack
        """
        damage = max(0, attacker.power - defender.defense)
        defender.take_damage(damage)

        self.event_bus.emit(CombatEvent(
            attacker=attacker,
            defender=defender,
            damage=damage
        ))

        return not defender.is_alive
```

## Common Pitfalls to Avoid

### ❌ Don't Do This

- **Batch multiple changes in one commit** - commit frequently instead
- **Skip tests** - test everything, always
- **Leave TODOs in code** - fix immediately or create a tracked task
- **Create god objects** - refactor before they grow too large
- **Tight coupling** - use events, protocols, and dependency injection
- **Hardcode values** - use configuration files or constants
- **Write cryptic variable names** - clarity over brevity
- **Accumulate technical debt** - refactor constantly

### ✅ Do This Instead

- **Commit after each small working change**
- **Write tests before/during implementation**
- **Fix issues immediately when noticed**
- **Extract responsibilities into focused classes**
- **Depend on abstractions via protocols**
- **Make entities/behaviors data-driven**
- **Use clear, descriptive names**
- **Refactor preemptively and often**

## Summary Checklist

Before committing ANY change, verify:

- [ ] All tests pass (`pytest tests/ -q`)
- [ ] New code has tests (one assertion per test)
- [ ] Code is well-organized and decoupled
- [ ] No god objects or classes over 200 lines
- [ ] Commit message is clear and succinct
- [ ] Only ONE logical change in this commit
- [ ] Code follows existing architecture patterns
- [ ] No TODOs or commented-out code left behind

## Questions?

When in doubt:
1. **Look at existing code** - follow established patterns
2. **Prioritize decoupling** - this is the #1 principle
3. **Write tests first** - they guide good design
4. **Commit often** - small, focused commits are better
5. **Refactor constantly** - don't let technical debt build

Remember: **Clean, decoupled, well-tested code** is the goal. Sacrifice speed for quality.
