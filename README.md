# Roguelike Game

A classic ASCII roguelike game built with Python and python-tcod, featuring procedural generation, turn-based combat, permadeath, character progression, a complete crafting system, and spell scrolls.

## Features

### Core Roguelike Features
- **Procedural Generation**: Each dungeon is randomly generated with rooms and corridors
- **Permadeath**: When you die, the game is over - no saves!
- **Turn-Based Combat**: Tactical combat where every move matters
- **Field of View**: See only what's in your line of sight, with explored areas shown dimly
- **Character Progression**: Gain XP by defeating monsters and level up to become stronger
- **Monster AI**: Enemies chase and attack the player when nearby
- **5 Dungeon Levels**: Descend deeper into progressively harder levels with stairs

### Game Systems

#### Combat & Progression
- **Multiple Monster Types**:
  - Orcs (o): Weak but common
  - Trolls (T): Stronger and tougher
  - Stats scale by dungeon level (up to 2x at level 5)
- **Combat System**: Attack power vs defense with damage calculation
- **Experience System**: Gain XP from kills, level up for stat increases
- **Health System**: Visual health bars showing HP for player and monsters

#### Items & Inventory
- **20+ Items**: Healing potions, buff potions, magic scrolls, and special items
- **Inventory System**: Pickup, drop, and use items (10 slot capacity)
- **Item Categories**:
  - **Healing**: Healing Potion, Greater Healing Potion, Cheese Wheel
  - **Buff Potions**: Strength, Defense, Speed, Invisibility, Gigantism, Shrinking
  - **Combat Scrolls**: Fireball, Lightning, Confusion
  - **Utility Scrolls**: Teleportation, Magic Mapping
  - **Special Items**: Lucky Coin, Cursed Ring, Coffee, Banana Peel, Rubber Chicken

#### Crafting System
- **36 Craftable Items**: 17 crafting materials + 19 craftable results
- **22 Crafting Recipes**: Create powerful items from materials found in dungeons
- **Tag-Based System**: Items matched by abstract qualities (herbal, magical, rare, etc.)
- **Recipe Discovery**: Track which recipes you've successfully crafted
- **Spell Crafting**: Create magical scrolls from parchment, runic essence, and elements
- **Categories**:
  - Basic potions (healing, mana, antidote)
  - Buff potions (strength, defense, speed, invisibility)
  - Combat scrolls (fireball, lightning, confusion)
  - Utility scrolls (teleportation, magic mapping)
  - Special items (lucky coin, cursed ring)
- See [CRAFTING_SYSTEM.md](CRAFTING_SYSTEM.md) for complete crafting guide

#### UI & Feedback
- **Message Log**: Scrolling message history showing combat, items, and events
- **Visual Health Bars**: Color-coded HP bars (green → yellow → red)
- **Smart Rendering**: Viewport clipping for performance optimization

## Installation

### Requirements
- Python 3.12 or higher
- uv (Python package manager)

### Setup

1. Navigate to the project directory:
```bash
cd claude-web-credit
```

2. Install dependencies:
```bash
uv pip install -e .
```

## How to Play

### Running the Game
```bash
uv run python main.py
```

Or with the virtual environment activated:
```bash
.venv/bin/python main.py
```

### Controls

#### Movement
- **Arrow Keys or hjkl**: Move in cardinal directions
- **yubn**: Move diagonally (vi keys)
  - y: up-left
  - u: up-right
  - b: down-left
  - n: down-right
- **.** (period): Wait/skip turn

#### Actions
- **g**: Pick up item from floor
- **i**: Open inventory to use items
- **d**: Drop item from inventory
- **>**: Descend stairs to next level
- **ESC**: Quit game

### Gameplay Tips

#### Combat
- **Fight strategically**: Sometimes it's better to retreat than fight multiple enemies
- **Level up**: Defeating monsters grants XP - leveling up increases your HP, power, and defense
- **Watch your HP**: Use healing items before it's too late
- **Use scrolls**: Fireball and Lightning scrolls can turn the tide of battle

#### Exploration
- **Explore carefully**: Your field of view is limited - be cautious around corners
- **Look for stairs**: Find the `>` symbol to descend to the next level
- **Collect materials**: Gather crafting materials (herbs, crystals, etc.) for crafting

#### Items & Crafting
- **Manage inventory**: You have 10 inventory slots - choose wisely
- **Craft powerful items**: Combine materials to create potions, scrolls, and special items
- **Magic scrolls**: Craft scrolls by combining parchment + runic essence + elemental components
- **Buff before boss fights**: Use strength/defense potions for tough encounters

### Game Symbols
- `@`: You (the player)
- `o`: Orc
- `T`: Troll
- `#`: Wall
- `.`: Floor
- `>`: Stairs down to next level
- `!`: Potion
- `?`: Scroll
- `%`: Food/Herb
- `*`: Crystal/Powder
- `=`: Ring
- `$`: Coin
- Dark areas: Unexplored
- Gray areas: Explored but not currently visible
- White areas: Currently visible

## Development

### Running Tests
```bash
uv run pytest tests/ -v
```

**565 passing tests** covering all major systems!

### Running Specific Test Suites
```bash
# Crafting system tests
uv run pytest tests/test_crafting*.py tests/test_recipe*.py -v

# Inventory system tests
uv run pytest tests/test_inventory*.py tests/test_item*.py -v

# Core game tests
uv run pytest tests/test_combat.py tests/test_level.py -v
```

### Project Structure
```
claude-web-credit/
├── src/roguelike/
│   ├── engine/         # Game loop, state management, events
│   ├── entities/       # Player, monsters, items
│   ├── world/          # Map, tiles, dungeon generation, FOV
│   ├── systems/        # Combat, AI, experience, inventory, crafting, levels
│   ├── components/     # Component-based architecture (health, combat, crafting, inventory)
│   ├── commands/       # Command pattern for actions (move, attack, pickup, use, craft)
│   ├── ui/             # Rendering, input handling, health bars, message log
│   ├── utils/          # Position and other utilities
│   └── data/           # JSON data files (entities, recipes, levels)
├── tests/              # Comprehensive test suite (464 tests)
├── main.py             # Entry point
├── CRAFTING_SYSTEM.md  # Complete crafting system documentation
├── DEVELOPMENT.md      # Development guidelines
└── pyproject.toml      # Project configuration
```

### Code Quality
- **565 passing tests** covering all major systems
- **Clean architecture** with component-based design
- **Event-driven** systems for decoupling
- **Data-driven** content (items, recipes, levels in JSON)
- **Type hints** throughout
- **Comprehensive docstrings**
- **Command pattern** for undo/redo support
- **Test-driven development** approach

## Technical Details

### Built With
- **Python 3.12**: Modern Python features
- **python-tcod 19.6.0**: Terminal rendering and FOV algorithms
- **numpy**: Efficient tile and FOV map storage
- **pytest**: Testing framework with 464 tests
- **uv**: Fast, modern Python package manager

### Architecture Highlights

#### Component-Based Design
- **ComponentEntity**: Flexible entity system using composition
- **CraftingComponent**: Tag-based crafting metadata
- **RecipeDiscoveryComponent**: Tracks discovered recipes
- **InventoryComponent**: Item storage and management
- **HealthComponent, CombatComponent, LevelComponent**: Core RPG stats

#### Event-Driven Architecture
- **EventBus**: Pub/sub pattern for system decoupling
- **Events**: Combat, Death, LevelUp, XP, Crafting, RecipeDiscovery, ItemPickup, ItemUse, Healing, etc.
- **Message Log**: Subscribes to events for player feedback

#### Data-Driven Content
- **entities.json**: 36+ items, 3 monster types, player definition
- **recipes.json**: 22 crafting recipes with tag-based matching
- **levels.json**: 5 dungeon level configurations with difficulty scaling

#### Systems Architecture
- **CraftingSystem**: Tag-based recipe matching, ingredient consumption
- **InventorySystem**: Item management with capacity limits
- **ItemSystem**: Item usage and effects
- **LevelSystem**: Multi-level dungeon with stairs
- **CombatSystem**: Damage calculation and resolution
- **AISystem**: Monster pathfinding and behavior

### Design Patterns
- **Component-Based Entity System**: Flexible, composable entities
- **Command Pattern**: Undoable actions for all player input
- **Event Bus**: Decoupled system communication
- **Strategy Pattern**: Different item effects and AI behaviors
- **Factory Pattern**: Entity and item creation from templates
- **Data-Driven Design**: JSON-based content definition

## Crafting System

The game features a complete tag-based crafting system inspired by acclaimed roguelikes like *Sulphur Memories: Alchemist*. Players can:

- Collect **17 different crafting materials** from dungeon exploration
- Craft **19 different items** using tag-based recipes
- Create **magical scrolls** by combining parchment, runic essence, and elemental components
- Brew **buff potions** for combat advantages
- Craft **healing items** and **special artifacts**

**Recipe Examples**:
- Healing Potion = Moonleaf (herbal) + Mana Crystal (magical)
- Scroll of Fireball = Phoenix Feather (fiery) + Ancient Parchment + Runic Essence
- Potion of Strength = Iron Ore (metallic) + Giant's Tears (empowering)
- Lucky Coin = Dragon Scale + Dragon Scale + Blessed Water (holy)

See [CRAFTING_SYSTEM.md](CRAFTING_SYSTEM.md) for complete documentation, all recipes, and integration guide.

## Recent Updates

### Recipe Discovery System (Latest)
- Track which recipes player has successfully crafted
- RecipeDiscoveryComponent integrated with player entity
- RecipeDiscoveredEvent for UI feedback
- Automatic discovery on successful crafting
- 24 new tests for recipe discovery functionality

### Crafting System
- Complete tag-based crafting with 36 items and 22 recipes
- Integration with existing item and spell systems
- Ingredient consumption and position handling
- Crafting events for UI feedback

### Content Integration
- 20+ items from item system now craftable
- Spell scrolls integrated into crafting
- Buff potions with various effects
- Special items (lucky coin, cursed ring)

### Core Systems
- Multi-level dungeons with 5 difficulty-scaled levels
- Inventory system with pickup/drop/use commands
- Message log with scrolling history
- Visual health bars for player and monsters
- Event bus for decoupled systems

## Future Enhancements

Potential additions:
- **Equipment System**: Weapons and armor with stats
- **Status Effects**: Poison, confusion, invisibility implementation
- **More Monster Types**: Unique abilities and behaviors
- **Traps**: Environmental hazards
- **Procedural Item Generation**: Random magical properties
- **Recipe Hints**: Display ingredients for discovered recipes
- **Crafting Quality**: Varying results based on ingredients
- **LLM-based NPCs**: Procedurally generated characters with AI dialogue

## Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for development guidelines, coding standards, and architecture patterns.

## License

MIT License - Feel free to use this code for learning or building your own roguelike!

## Credits

Inspired by classic roguelikes and modern innovations:
- **NetHack**: Complexity and depth
- **DCSS (Dungeon Crawl Stone Soup)**: Streamlined systems
- **Brogue**: Elegant design and emergent gameplay
- **Sulphur Memories: Alchemist**: Tag-based crafting philosophy
- **Alchemist's Alcove**: Recipe discovery mechanics
