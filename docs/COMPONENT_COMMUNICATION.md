# Component Communication Patterns

This document describes how components communicate in this roguelike game, based on the Component pattern from [Game Programming Patterns](https://gameprogrammingpatterns.com/component.html).

## Overview

This codebase uses the **Component pattern** for entity composition. Entities are built from composable components that encapsulate specific behaviors (health, combat, inventory, etc.).

## Communication Strategies

The book describes three main communication strategies. This codebase primarily uses **Shared State** with some **Messaging** at the system level.

### 1. Shared State (Primary Pattern)

**How it works:**
- Components are accessed via `entity.get_component(ComponentType)`
- Systems orchestrate interactions between components
- Components themselves don't directly reference other components

**Advantages:**
- Clear separation of concerns
- Components remain loosely coupled
- Easy to add/remove components dynamically

**Disadvantages:**
- Requires null checks when accessing components
- Processing order matters (see below)

**Example:**
```python
# EquipmentSystem modifies CombatComponent based on EquipmentStats
equipment_stats = item.get_component(EquipmentStats)
combat_comp = entity.get_component(CombatComponent)
if combat_comp and equipment_stats:
    combat_comp.power += equipment_stats.power_bonus
```

### 2. Direct References (Not Used)

This pattern where components hold references to each other is **NOT used** in this codebase to maintain loose coupling.

### 3. Messaging (System-Level Only)

**How it works:**
- Systems emit events via `EventBus` for notifications
- Components themselves don't use messaging
- Used for game events (combat, death, level-up, etc.)

**Example:**
```python
# StatusEffectsSystem emits events
self.event_bus.emit(
    StatusEffectAppliedEvent(
        entity_name=entity.name,
        effect_type=effect_type,
        duration=duration,
    )
)
```

## Component Dependencies

### Who Modifies What

Understanding which systems modify which components is critical for avoiding race conditions.

| System | Modifies | Why |
|--------|----------|-----|
| **StatusEffectsSystem** | HealthComponent | Applies poison damage per turn |
| **EquipmentSystem** | CombatComponent, HealthComponent | Applies/removes stat bonuses from equipment |
| **CombatSystem** | HealthComponent, LevelComponent | Applies damage, awards XP |
| **ComponentEntity** | All (via properties) | Provides convenient property access |

### Shared Mutable State Warning

As the book warns: *"Shared mutable state where lots of code is reading and writing the same data is notoriously hard to get right."*

**Components with shared mutable state:**
- **HealthComponent**: Modified by StatusEffectsSystem, EquipmentSystem, CombatSystem
- **CombatComponent**: Modified by EquipmentSystem (bonuses), read by CombatSystem

## Processing Order

**The book advises: "Document and enforce this order explicitly."**

### Turn Processing Order

The processing order is **critical** to avoid race conditions:

1. **Player Action** (may involve combat → modifies HealthComponent)
2. **Player Status Effects** (StatusEffectsSystem → modifies HealthComponent)
3. **Enemy AI Turns** (may involve combat → modifies HealthComponent)
4. **Enemy Status Effects** (StatusEffectsSystem → modifies HealthComponent)

### Equipment Bonus Application Order

When equipping/unequipping items:

1. **Unequip old item** (if slot occupied)
   - Remove stat bonuses from CombatComponent
   - Adjust max HP in HealthComponent (maintains HP percentage)
2. **Equip new item**
   - Add stat bonuses to CombatComponent
   - Adjust max HP in HealthComponent (maintains HP percentage)

**Important:** Equipment bonuses are applied directly to component stats. This means:
- `CombatComponent.power` includes equipment bonuses
- `HealthComponent.max_hp` includes equipment bonuses
- No need to recalculate bonuses each frame

### Status Effect Processing Order

When processing effects (see StatusEffectsSystem.process_effects):

1. **Apply effect behavior** (e.g., poison damage)
2. **Check if entity died** → if yes, clear all effects and return
3. **Emit tick events** (for surviving entities)
4. **Decrement durations** and remove expired effects
5. **Emit expiration events**

## Component Communication Guidelines

### DO:
✅ Use `entity.get_component(Type)` to access components
✅ Check for `None` when getting components that might not exist
✅ Use ComponentEntity properties (`entity.hp`, `entity.power`) for convenience
✅ Emit events via EventBus for notifications
✅ Document processing order in system docstrings

### DON'T:
❌ Store direct references between components
❌ Modify components from other components
❌ Assume a component exists without checking
❌ Create circular dependencies between components

## Accessing Entity Data

There are three ways to access entity data:

### 1. ComponentEntity Properties (Recommended for common stats)
```python
# Direct property access (raises AttributeError if component missing)
hp = entity.hp
power = entity.power
```

### 2. Direct Component Access (Recommended for complex operations)
```python
# Get component, check for None
health = entity.get_component(HealthComponent)
if health:
    health.take_damage(10)
```

### 3. Helper Functions (Recommended for type checking)
```python
# Safe helpers that handle component existence
if is_alive(entity) and is_monster(entity):
    process_monster_ai(entity)
```

## Best Practices

1. **Keep Components Simple**: Components should store state, not complex behavior
2. **Systems Orchestrate**: Put behavior in Systems, not Components
3. **Document Dependencies**: If a system modifies multiple components, document it
4. **Maintain Processing Order**: Don't reorder turn processing without careful analysis
5. **Use Events for Notifications**: Don't couple systems directly for notifications

## Future Considerations

As the game grows, consider:

- **Component Queries**: If filtering entities by components becomes common, add a query system
- **Component Lifecycle**: If components need initialization/cleanup, add lifecycle methods
- **Performance**: If component access becomes a bottleneck, consider caching frequently accessed components
