# Crafting System

A complete, modular, tag-based crafting system inspired by acclaimed roguelikes like *Sulphur Memories: Alchemist* and *Alchemist's Alcove*.

## Overview

The crafting system allows players to combine items to create new items through recipe-based crafting. The system is:

- **Tag-Based**: Items are matched by abstract qualities (tags) rather than specific types
- **Modular**: Fully decoupled, event-driven architecture
- **Data-Driven**: All recipes and items defined in JSON files
- **Extensible**: Easy to add new items and recipes without code changes

### Content Summary

- **36 total items** (17 materials + 19 craftable results)
- **22 crafting recipes** covering multiple categories
- **Integrated spell/magic system** via craftable scrolls
- **Buff potions** for combat enhancement
- **Advanced healing items** for survivability
- **Special items** with unique effects

## Architecture

### Components

#### CraftingComponent (`src/roguelike/components/crafting.py`)

Adds crafting capabilities to items. Each item with this component has:
- **tags**: Set of quality descriptors (e.g., `{"herbal", "magical"}`)
- **consumable**: Whether the item is consumed when used in crafting
- **craftable**: Whether this item can be crafted (vs. found only)

#### Recipe (`src/roguelike/systems/crafting.py`)

Defines how to combine ingredients:
- **id**: Unique recipe identifier
- **name**: Display name
- **required_tags**: List of tag sets that ingredients must match
- **result_type**: Entity type to create as result
- **description**: Recipe description

Recipes match ingredients in **any order** and support **multiple tags per ingredient**.

#### CraftingSystem (`src/roguelike/systems/crafting.py`)

Main crafting logic:
- `find_matching_recipe()`: Finds recipe matching given ingredients
- `can_craft()`: Checks if ingredients can be crafted
- `craft(ingredients, crafter, position)`: Performs crafting, creates result, returns consumed ingredients

**Return Value**:
`craft()` returns a tuple: `(result_item, consumed_ingredients)`
- `result_item`: The crafted item entity (or None if crafting failed)
- `consumed_ingredients`: List of ingredients marked as consumable that should be removed from inventory/map

**Ingredient Consumption**:
- Ingredients with `consumable=True` in their CraftingComponent are included in the consumed list
- Non-consumable ingredients (tools like a mortar & pestle) are NOT consumed and can be reused
- **Caller is responsible** for removing consumed ingredients from inventory or destroying them on the map
- This maintains decoupling - the crafting system doesn't need to know about inventory management

**Position Handling**:
The `craft()` method requires a spawn position for the crafted item. Position is determined by priority:
1. **Explicit `position` parameter** - If provided, always used
2. **Crafter's position** - If crafter is provided, uses their current position
3. **Fails** - Returns (None, []) if neither is available

**Important**: Items that have been picked up retain their map coordinates from when they were on the floor. Therefore, **never use ingredient positions** - always provide either a crafter or explicit position to ensure crafted items spawn at the correct location (typically where the player is).

#### RecipeLoader (`src/roguelike/data/recipe_loader.py`)

Loads recipes from JSON:
- Parses `recipes.json` into Recipe objects
- Supports custom recipe file paths
- Hot-reloadable for development

### Events

Crafting operations emit events via the EventBus:

- **CraftingAttemptEvent**: Emitted when crafting is attempted
  - `crafter_name`: Who is crafting
  - `ingredient_names`: What ingredients were used
  - `success`: Whether crafting succeeded
  - `result_name`: Name of result item (if successful)

- **RecipeDiscoveredEvent**: Emitted when a new recipe is discovered
  - `recipe_id`: ID of discovered recipe
  - `recipe_name`: Name of recipe
  - `discoverer_name`: Who discovered it

## Data Files

### recipes.json

Defines all crafting recipes:

```json
{
  "healing_potion": {
    "name": "Healing Potion",
    "required_tags": [
      ["herbal"],
      ["magical"]
    ],
    "result_type": "healing_potion",
    "description": "Combines herbs and magic to create a healing elixir"
  }
}
```

**Tag Format**: Each ingredient is a list of required tags. The ingredient must have ALL tags in its list to match.

**Example**:
- `[["herbal"], ["magical"]]` - Two ingredients, one with "herbal" tag, one with "magical" tag
- `[["herbal", "magical"], ["rare"]]` - Two ingredients, first must have BOTH "herbal" AND "magical", second must have "rare"

### entities.json

Defines craftable items and materials:

```json
{
  "moonleaf": {
    "char": "%",
    "name": "Moonleaf",
    "blocks_movement": false,
    "components": {
      "crafting": {
        "tags": ["herbal", "verdant"],
        "consumable": true,
        "craftable": false
      }
    }
  }
}
```

## Available Items

### Crafting Materials (found in dungeon)

| Item | Tags | Description |
|------|------|-------------|
| Moonleaf | herbal, verdant | Healing herb |
| Mana Crystal | magical, crystalline | Magic essence |
| Nightshade | herbal, sinister | Dark poison herb |
| Purifying Salt | purifying, crystalline | Cleansing agent |
| Iron Ore | metallic | Base metal |
| Volcanic Ash | volcanic | Fire element |
| Sulfur | sulfuric, volcanic | Explosive element |
| Frost Essence | boreal, crystalline | Ice element |
| Dragon Scale | rare, magical | Rare magic item |
| Runic Essence | magical, runic | Ancient magic runes |
| Ancient Parchment | parchment, ancient | Blank scroll base |
| Phoenix Feather | rare, fiery, magical | Fire magic component |
| Thunder Stone | rare, electric, crystalline | Lightning magic component |
| Shadow Ink | sinister, liquid | Dark magic ink |
| Blessed Water | purifying, liquid, holy | Holy water |
| Giant's Tears | rare, liquid, empowering | Strength essence |
| Pixie Dust | magical, ethereal | Invisibility component |
| Coffee | liquid, energizing | Energy boost ingredient |

### Craftable Results

#### Basic Potions & Items
| Item | Recipe | Description |
|------|--------|-------------|
| Healing Potion | herbal + magical | Restores health |
| Mana Potion | magical + crystalline | Restores mana |
| Antidote | herbal + purifying | Cures poison |
| Strength Elixir | herbal + magical + rare | Boosts strength |
| Spark Powder | volcanic + sulfuric | Fire damage |
| Ice Shard | crystalline + boreal | Ice weapon |
| Poison Blade | metallic + sinister | Poisoned weapon |

#### Advanced Healing
| Item | Recipe | Description |
|------|--------|-------------|
| Greater Healing Potion | herbal + herbal + holy | Powerful healing |
| Cheese Wheel | (herbal+verdant) + purifying | Large heal food |

#### Buff Potions
| Item | Recipe | Description |
|------|--------|-------------|
| Potion of Strength | metallic + empowering | +3 power boost |
| Potion of Defense | (rare+magical) + purifying | +3 defense boost |
| Potion of Speed | energizing + magical | Double actions |
| Potion of Invisibility | ethereal + sinister | 10 turns invisible |
| Potion of Gigantism | empowering + magical | +5 power boost |
| Potion of Shrinking | ethereal + boreal | +3 defense boost |

#### Combat Scrolls (Spell System)
| Item | Recipe | Description |
|------|--------|-------------|
| Scroll of Fireball | fiery + parchment + runic | 25 damage AoE |
| Scroll of Lightning | electric + parchment + runic | 20 damage single target |
| Scroll of Confusion | (sinister+liquid) + parchment + runic | 10 turns confusion |

#### Utility Scrolls (Spell System)
| Item | Recipe | Description |
|------|--------|-------------|
| Scroll of Teleportation | (magical+crystalline) + parchment + runic | Random teleport |
| Scroll of Magic Mapping | (magical+crystalline) + parchment + holy | Reveals map |

#### Special Items
| Item | Recipe | Description |
|------|--------|-------------|
| Lucky Coin | (rare+magical) + (rare+magical) + holy | 50% XP bonus |
| Cursed Ring | sinister + metallic + (sinister+liquid) | Random curse |

## Usage Example

```python
from roguelike.systems.crafting import CraftingSystem
from roguelike.data.recipe_loader import RecipeLoader
from roguelike.data.entity_loader import EntityLoader
from roguelike.engine.events import EventBus
from roguelike.utils.position import Position

# Initialize system
recipe_loader = RecipeLoader()
event_bus = EventBus()
crafting_system = CraftingSystem(
    recipe_loader=recipe_loader,
    event_bus=event_bus
)

# Load items
entity_loader = EntityLoader()
moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

# Create player with inventory
player = entity_loader.create_entity("player", Position(10, 10))
from roguelike.systems.inventory import Inventory
inventory = Inventory(capacity=10)
inventory.add(moonleaf)
inventory.add(crystal)

# Check if craftable
if crafting_system.can_craft([moonleaf, crystal]):
    # Perform crafting - returns result and consumed ingredients
    result, consumed = crafting_system.craft([moonleaf, crystal], crafter=player)

    if result:
        print(f"Crafted: {result.name}")  # "Crafted: Healing Potion"
        print(f"Position: {result.position}")  # "Position: Position(10, 10)"

        # Remove consumed ingredients from inventory
        for ingredient in consumed:
            inventory.remove(ingredient)

        # Add crafted item to inventory
        inventory.add(result)

# Alternative: Specify explicit position
result, consumed = crafting_system.craft(
    [moonleaf, crystal],
    crafter=player,
    position=Position(15, 15)  # Spawn at specific location
)

# Handle consumed ingredients
for ingredient in consumed:
    inventory.remove(ingredient)
```

## Design Philosophy

### Tag-Based Flexibility

Instead of hardcoding "Moonleaf + Mana Crystal = Healing Potion", we use abstract qualities:
- "herbal" can be moonleaf, nightshade, or any future herb
- "magical" can be mana crystal, dragon scale, or any magic item
- This allows **multiple valid combinations** and **recipe discovery**

### Inspired By

- **Sulphur Memories: Alchemist**: Raw materials have abstract qualities like "something sinister" or "something verdant"
- **Alchemist's Alcove**: Combine 2-3 items to discover recipes
- **Brogue**: Focus on item interactions and emergent gameplay
- **DCSS**: Streamlined systems with meaningful choices

### Modular Architecture

The system follows the codebase's architectural patterns:
- **Event-driven**: All crafting operations emit events
- **Component-based**: Items compose behavior via CraftingComponent
- **Data-driven**: All recipes/items in JSON, no hardcoding
- **Decoupled**: CraftingSystem doesn't know about inventory, UI, or game engine

## Testing

The crafting system has **48 tests** covering:
- Component creation and tag matching
- Recipe loading and parsing
- Recipe matching logic (order-independent, multi-tag)
- Crafting operations (success, failure, events)
- Entity loading with crafting data

Run tests:
```bash
uv run pytest tests/test_crafting*.py tests/test_recipe*.py -v
```

## Extending the System

### Adding New Materials

1. Add item to `src/roguelike/data/entities.json`:
```json
"ruby": {
  "char": "*",
  "name": "Ruby",
  "blocks_movement": false,
  "components": {
    "crafting": {
      "tags": ["crystalline", "fiery", "rare"],
      "consumable": true,
      "craftable": false
    }
  }
}
```

2. No code changes needed!

### Adding New Recipes

1. Add recipe to `src/roguelike/data/recipes.json`:
```json
"fire_gem": {
  "name": "Fire Gem",
  "required_tags": [
    ["crystalline", "fiery"],
    ["volcanic"]
  ],
  "result_type": "fire_gem",
  "description": "A gem infused with volcanic fire"
}
```

2. Add result item to `entities.json`

3. No code changes needed!

### Adding New Tag Types

Tags are completely freeform. Just use them in entities and recipes:
- `"aquatic"` for water-based items
- `"ethereal"` for ghost/spirit items
- `"cursed"` for dark magic
- `"blessed"` for holy items

The system automatically handles any tags you define.

## Future Enhancements

Potential extensions (not yet implemented):
- Recipe discovery (track which recipes player has found)
- Crafting requirements (tools, stations, skills)
- Crafting quality (varying result based on ingredients)
- Partial matches (use similar tags if exact match unavailable)
- Crafting XP (gain experience from crafting)
- Recipe hints (show partial recipe requirements)

## Integration Points

To integrate with game systems:

1. **Inventory System**: Call `crafting_system.craft()` with selected items
2. **UI System**: Subscribe to `CraftingAttemptEvent` to show feedback
3. **Item System**: Craftable items can have additional components (consumable, equippable, etc.)
4. **Command System**: Create `CraftCommand` for undo/redo support

## File Structure

```
src/roguelike/
├── components/
│   └── crafting.py          # CraftingComponent
├── systems/
│   └── crafting.py          # Recipe, CraftingSystem
├── data/
│   ├── recipes.json         # Recipe definitions
│   ├── recipe_loader.py     # RecipeLoader
│   ├── entities.json        # Item definitions (updated)
│   └── entity_loader.py     # EntityLoader (updated)
└── engine/
    └── events.py            # CraftingEvents (updated)

tests/
├── test_crafting_component.py  # 9 tests
├── test_crafting_events.py     # 5 tests
├── test_crafting_system.py     # 16 tests
├── test_recipe.py              # 10 tests
└── test_recipe_loader.py       # 8 tests
```

## Summary

The crafting system provides a flexible, modular foundation for item creation. Its tag-based approach allows for emergent gameplay and easy content expansion, while maintaining clean separation from other game systems through events and components.
