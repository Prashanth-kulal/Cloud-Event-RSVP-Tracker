"""
Real-Time Service — WebSocket Manager for local development.

Cloud equivalent: Firestore real-time listeners.

This module manages a set of WebSocket connections subscribed to
specific event channels. When an RSVP is created, updated, or deleted,
the RSVP service calls broadcast_rsvp_update() which pushes the new
RSVP counts to all connected clients subscribed to that event.

THREE APPROACHES TO REAL-TIME (documented for cloud computing comparison):

1. POLLING
   - Client repeatedly calls GET /api/events/{id}/analytics every N seconds.
   - Simple to implement; high server load; not truly real-time.
   - Used in: legacy web apps.

2. SERVER-SENT EVENTS (SSE)
   - One-way HTTP stream from server to client.
   - Browser's EventSource API.
   - Good for dashboards; no bi-directional communication.
   - Fallback when WebSockets are blocked.

3. WEBSOCKETS (IMPLEMENTED HERE for local dev)
   - Full-duplex persistent connection.
   - Client subscribes to event channel.
   - Server pushes updates instantly.
   - Cloud equivalent: Firebase/Firestore real-time listeners.

In production (cloud):
   - Firestore's onSnapshot() replaces WebSocket entirely.
   - Managed, serverless, scales globally.
"""
import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("realtime")


class ConnectionManager:
    """Manages WebSocket connections grouped by event_id channel."""

    def __init__(self):
        # Maps event_id -> list of active WebSocket connections
        self._channels: Dict[str, List[WebSocket]] = {}

    async def connect(self, event_id: str, websocket: WebSocket):
        await websocket.accept()
        if event_id not in self._channels:
            self._channels[event_id] = []
        self._channels[event_id].append(websocket)
        logger.info("WebSocket connected to event channel: %s (total: %d)",
                    event_id, len(self._channels[event_id]))

    def disconnect(self, event_id: str, websocket: WebSocket):
        if event_id in self._channels:
            try:
                self._channels[event_id].remove(websocket)
            except ValueError:
                pass
            if not self._channels[event_id]:
                del self._channels[event_id]
        logger.info("WebSocket disconnected from event channel: %s", event_id)

    async def broadcast_to_event(self, event_id: str, message: dict):
        """Send a JSON message to all subscribers of an event channel."""
        if event_id not in self._channels:
            return
        dead = []
        for ws in self._channels[event_id]:
            try:
                await ws.send_text(json.dumps(message))
            except Exception as exc:
                logger.warning("Failed to send WebSocket message: %s", exc)
                dead.append(ws)
        for ws in dead:
            self.disconnect(event_id, ws)

    async def broadcast_rsvp_update(self, event_id: str, counts: dict):
        """Broadcast updated RSVP counts to all subscribers of an event."""
        await self.broadcast_to_event(event_id, {
            "type": "RSVP_UPDATE",
            "event_id": event_id,
            "data": counts
        })

    async def broadcast_announcement(self, event_id: str, announcement: dict):
        """Broadcast a new announcement to all subscribers of an event."""
        await self.broadcast_to_event(event_id, {
            "type": "ANNOUNCEMENT",
            "event_id": event_id,
            "data": announcement
        })

    async def broadcast_event_status(self, event_id: str, status: str):
        """Broadcast event status change (e.g., FULL, CANCELLED)."""
        await self.broadcast_to_event(event_id, {
            "type": "EVENT_STATUS",
            "event_id": event_id,
            "data": {"status": status}
        })

    def get_subscriber_count(self, event_id: str) -> int:
        return len(self._channels.get(event_id, []))


# Singleton instance — shared across all route handlers
manager = ConnectionManager()
