"""Demonstration of EventSource and PresentationContext abstractions.

This example shows how the abstractions work without requiring a full
WebSocket server implementation.
"""

import asyncio
import tcod
import tcod.event

from roguelike.server.event_source import (
    EventSource,
    LocalEventSource,
    WebSocketEventSource,
    WebSocketEventBridge,
)
from roguelike.ui.presentation_context import (
    PresentationContext,
    TcodPresentationContext,
    WebSocketPresentationContext,
)


# Mock GameServer for testing
class MockGameServer:
    """Minimal mock server for testing abstractions."""

    def __init__(self):
        self.input_queue = asyncio.Queue()
        self.broadcast_history = []

    async def get_input(self, timeout=0.1):
        """Simulate receiving browser input."""
        try:
            return await asyncio.wait_for(self.input_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def broadcast(self, data):
        """Simulate sending frame to browser."""
        self.broadcast_history.append(data)
        print(f"[MockServer] Broadcast: {data.get('type', 'unknown')}")

    async def simulate_browser_input(self, key):
        """Simulate browser sending a key press."""
        await self.input_queue.put({"type": "keydown", "key": key})


def test_event_bridge():
    """Test browser event → tcod event translation."""
    print("\n=== Testing WebSocketEventBridge ===\n")

    bridge = WebSocketEventBridge()

    # Test various browser key events
    test_cases = [
        {"key": "ArrowUp", "expected": tcod.event.KeySym.UP},
        {"key": "k", "expected": tcod.event.KeySym.K},
        {"key": "i", "expected": tcod.event.KeySym.I},
        {"key": "Escape", "expected": tcod.event.KeySym.ESCAPE},
        {"key": "unknown_key", "expected": None},
    ]

    for case in test_cases:
        message = {"type": "keydown", "key": case["key"]}
        event = bridge.browser_to_tcod_event(message)

        if case["expected"] is None:
            assert event is None, f"Expected None for {case['key']}"
            print(f"✓ {case['key']:15} → None (unmapped key)")
        else:
            assert isinstance(event, tcod.event.KeyDown)
            assert event.sym == case["expected"]
            print(f"✓ {case['key']:15} → {case['expected'].name}")

    # Test quit event
    quit_event = bridge.browser_to_tcod_event({"type": "quit"})
    assert isinstance(quit_event, tcod.event.Quit)
    print(f"✓ quit event    → tcod.event.Quit")

    print("\n✅ Event bridge tests passed!\n")


async def test_event_source():
    """Test WebSocketEventSource."""
    print("\n=== Testing WebSocketEventSource ===\n")

    server = MockGameServer()
    event_source = WebSocketEventSource(server)

    # Simulate browser sending keys
    await server.simulate_browser_input("k")
    await server.simulate_browser_input("i")
    await server.simulate_browser_input("Escape")

    # Get events
    events1 = await event_source.get_events(timeout=0.1)
    assert len(events1) == 1
    assert events1[0].sym == tcod.event.KeySym.K
    print(f"✓ Received event: K")

    events2 = await event_source.get_events(timeout=0.1)
    assert len(events2) == 1
    assert events2[0].sym == tcod.event.KeySym.I
    print(f"✓ Received event: I")

    events3 = await event_source.get_events(timeout=0.1)
    assert len(events3) == 1
    assert events3[0].sym == tcod.event.KeySym.ESCAPE
    print(f"✓ Received event: ESCAPE")

    # No more events (timeout)
    events4 = await event_source.get_events(timeout=0.1)
    assert len(events4) == 0
    print(f"✓ Timeout works (no events)")

    print("\n✅ Event source tests passed!\n")


async def test_presentation_context():
    """Test WebSocketPresentationContext."""
    print("\n=== Testing WebSocketPresentationContext ===\n")

    server = MockGameServer()
    context = WebSocketPresentationContext(
        game_server=server, width=10, height=5
    )

    # Create a simple console
    console = tcod.console.Console(10, 5)
    console.print(0, 0, "Hello", fg=(255, 255, 255))
    console.print(0, 1, "World", fg=(100, 200, 100))

    # Present console (should broadcast frame)
    context.present(console)

    # Give async task time to execute
    await asyncio.sleep(0.1)

    # Check broadcast happened
    assert len(server.broadcast_history) > 0
    frame = server.broadcast_history[-1]

    assert frame["type"] == "frame"
    assert frame["width"] == 10
    assert frame["height"] == 5
    assert "tiles" in frame
    assert "ch" in frame["tiles"]
    assert "fg" in frame["tiles"]
    assert "bg" in frame["tiles"]

    print(f"✓ Frame broadcast successful")
    print(f"  - Type: {frame['type']}")
    print(f"  - Size: {frame['width']}x{frame['height']}")
    print(f"  - Tiles: {len(frame['tiles']['ch'])} rows")

    # Test close notification
    context.close()
    await asyncio.sleep(0.1)

    close_message = server.broadcast_history[-1]
    assert close_message["type"] == "close"
    print(f"✓ Close notification sent")

    print("\n✅ Presentation context tests passed!\n")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  EventSource & PresentationContext Abstraction Tests")
    print("=" * 60)

    # Test event translation
    test_event_bridge()

    # Test event source
    await test_event_source()

    # Test presentation context
    await test_presentation_context()

    print("=" * 60)
    print("  ✅ All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
