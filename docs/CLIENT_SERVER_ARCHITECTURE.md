# Client/Server Architecture Design

This document describes the abstraction layers for running the game in client/server mode via WebSocket.

## Overview

The architecture uses two symmetric abstractions:

1. **EventSource** - Input layer (keyboard/mouse events)
2. **PresentationContext** - Output layer (rendering)

Both abstractions allow the game to run either **locally** (traditional tcod window) or **remotely** (browser via WebSocket) without changing core game logic.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Game Engine                           │
│                     (unchanged logic)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input Layer              │          Output Layer           │
│  ┌──────────────┐         │         ┌──────────────┐       │
│  │ EventSource  │◄────────┼────────►│ Presentation │       │
│  │  (abstract)  │         │         │   Context    │       │
│  └──────┬───────┘         │         └──────┬───────┘       │
│         │                 │                │                │
│    ┌────┴────┐            │           ┌────┴────┐          │
│    │         │            │           │         │           │
│  ┌─▼──┐  ┌──▼───┐        │        ┌──▼──┐  ┌──▼────┐      │
│  │Local│  │WebSkt│        │        │Tcod │  │WebSkt │      │
│  └─────┘  └──────┘        │        └─────┘  └───────┘      │
│                           │                                 │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. EventSource Abstraction

Located in: `src/roguelike/server/event_source.py`

**Interface:**
```python
class EventSource(ABC):
    async def get_events(self, timeout: float) -> List[tcod.event.Event]:
        """Get events in tcod format."""
```

**Implementations:**

- **LocalEventSource**: Calls `tcod.event.wait()` to get keyboard/mouse events from local window
- **WebSocketEventSource**: Receives browser events via WebSocket, translates to `tcod.event.KeyDown` objects

**Key Design Decision:** Browser events are **translated to tcod events** at the boundary, so InputHandler remains completely unchanged.

### 2. PresentationContext Abstraction

Located in: `src/roguelike/ui/presentation_context.py`

**Interface:**
```python
class PresentationContext(ABC):
    def present(self, console: tcod.console.Console) -> None:
        """Present console to target."""

    def close(self) -> None:
        """Close context."""
```

**Implementations:**

- **TcodPresentationContext**: Wraps `tcod.context.Context`, calls `context.present(console)` to show in local window
- **WebSocketPresentationContext**: Serializes `console._tiles` to JSON, broadcasts via WebSocket to browser clients

### 3. GameServer (Interface Stub)

Located in: `src/roguelike/server/game_server.py`

**Interface:**
```python
class GameServer:
    async def broadcast(self, data: dict) -> None:
        """Send frame data to all browser clients."""

    async def get_input(self, timeout: float) -> Optional[dict]:
        """Receive input from browser client."""

    async def start(self, host: str, port: int) -> None:
        """Start WebSocket server."""
```

**Status:** Currently just an interface stub. Full WebSocket implementation pending.

## Usage Examples

### Local Mode (Traditional)

```python
# Create local event source
event_source = LocalEventSource()

# Create renderer with local tcod context
renderer = Renderer(width=80, height=50)
# (Renderer creates TcodPresentationContext internally)

# Game loop
while running:
    # Get events from local keyboard/mouse
    for event in await event_source.get_events():
        input_handler.dispatch(event)

    # ... execute commands ...

    # Render to local window
    renderer.render(...)
    renderer.present()  # Calls TcodPresentationContext.present()
```

### WebSocket Mode (Browser)

```python
# Create WebSocket server
game_server = GameServer()

# Create WebSocket event source
event_source = WebSocketEventSource(game_server)

# Create WebSocket presentation context
presentation_context = WebSocketPresentationContext(
    game_server=game_server,
    width=80,
    height=50
)

# Create renderer with WebSocket context
renderer = Renderer(
    width=80,
    height=50,
    presentation_context=presentation_context  # Override default
)

# Start server in background
asyncio.create_task(game_server.start(host="0.0.0.0", port=8765))

# Game loop
while running:
    # Get events from browser via WebSocket
    for event in await event_source.get_events():
        input_handler.dispatch(event)  # Same InputHandler!

    # ... execute commands ...

    # Render to browser clients
    renderer.render(...)
    renderer.present()  # Calls WebSocketPresentationContext.present()
```

## Event Translation

### Browser → tcod Event Flow

```
Browser:
  User presses "k"
    ↓
  JavaScript captures keydown event
    ↓
  {"type": "keydown", "key": "k"}
    ↓
  WebSocket send to server

Server:
  WebSocketEventSource.get_events()
    ↓
  WebSocketEventBridge.browser_to_tcod_event()
    ↓
  tcod.event.KeyDown(sym=tcod.event.KeySym.K)
    ↓
  InputHandler.dispatch(event)  ← Same as local mode!
    ↓
  Creates MoveCommand(dx=0, dy=-1)
```

**Key Insight:** InputHandler sees identical events whether running locally or via WebSocket!

## Frame Serialization

### Console → Browser Flow

```
Server:
  Renderer.present()
    ↓
  WebSocketPresentationContext.present(console)
    ↓
  Serialize console._tiles to JSON:
    {
      "type": "frame",
      "width": 80,
      "height": 50,
      "tiles": {
        "ch": [[...], [...], ...],    # 2D array of character codes
        "fg": [[...], [...], ...],    # 2D array of RGB tuples
        "bg": [[...], [...], ...]     # 2D array of RGB tuples
      }
    }
    ↓
  WebSocket broadcast to all clients

Browser:
  Receive frame data
    ↓
  For each (x, y) in grid:
    - Draw background color
    - Draw character with foreground color
    ↓
  Canvas updated
```

## Optimization Opportunities

### Delta Encoding

Currently, full frame is sent (~40KB per frame). Can optimize with delta encoding:

```python
def _serialize_console(self, console):
    if self._prev_tiles is None:
        # First frame: send everything
        return {"type": "full", "tiles": {...}}
    else:
        # Find changed tiles
        changed = np.where(tiles != self._prev_tiles)

        # Send only differences
        return {
            "type": "delta",
            "changes": [
                {"x": x, "y": y, "ch": ch, "fg": fg, "bg": bg}
                for (x, y) in zip(changed[0], changed[1])
            ]
        }
```

**Typical savings:** 50-500 bytes per frame instead of 40KB

### Binary Protocol

Replace JSON with binary format (MessagePack, Protocol Buffers, or custom):

- Faster serialization
- Smaller payload
- More complex implementation

### Compression

Apply gzip/zlib compression to frames:

- Works well with JSON (text compresses nicely)
- Adds CPU overhead
- Good for slow connections

## Next Steps

1. **Implement GameServer** with WebSocket support (using `websockets` library)
2. **Modify Renderer** to accept optional `PresentationContext` parameter
3. **Create async game loop** in GameEngine that uses EventSource
4. **Build browser client** (HTML + Canvas + WebSocket)
5. **Add delta encoding** to WebSocketPresentationContext
6. **Test and optimize** latency and bandwidth

## Design Decisions

### Why translate browser events to tcod events?

**Alternative:** Create WebSocketInputHandler that directly creates Commands from browser input

**Chosen approach:** Translate to tcod events first

**Rationale:**
- ✅ Zero changes to InputHandler (reuse all logic)
- ✅ Translation layer is simple (~50 lines)
- ✅ Easy to add new keys (just update KEY_MAP)
- ✅ Both modes use same code path (easier to debug)

### Why inject PresentationContext into Renderer?

**Alternative:** Create WebSocketRenderer subclass

**Chosen approach:** Inject context via parameter

**Rationale:**
- ✅ Renderer class unchanged (no subclassing needed)
- ✅ Composition over inheritance
- ✅ Easy to switch contexts at runtime
- ✅ Default behavior preserved (creates local context if none provided)

## Open Questions

1. **Multiple clients:** Should each client get their own game instance, or can multiple clients spectate one game?
   - Initial: One game per client (simpler)
   - Future: Spectator mode, multiplayer

2. **Authentication:** How to prevent unauthorized access?
   - Initial: No auth (trust local network)
   - Future: Token-based auth, session management

3. **Reconnection:** What happens if WebSocket disconnects?
   - Initial: Game ends
   - Future: Reconnection with state recovery

4. **Latency:** How much latency is acceptable?
   - Target: <50ms for responsive feel
   - Acceptable: <100ms for turn-based game
   - Unacceptable: >200ms feels sluggish

5. **Rendering strategy:** Full frames vs delta encoding?
   - Initial: Full frames (simple, ~40KB per frame at 60 FPS = 2.4 MB/s)
   - Future: Delta encoding (50-500 bytes per frame)
