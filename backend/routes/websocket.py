"""
WebSocket route for real-time RSVP subscriptions.
ws://localhost:8000/ws/events/{event_id}

Client connects and receives JSON push messages whenever:
 - An RSVP is created/updated/deleted (type: RSVP_UPDATE)
 - An announcement is posted (type: ANNOUNCEMENT)
 - Event status changes (type: EVENT_STATUS, EVENT_UPDATED)

Cloud equivalent: Firestore onSnapshot() listener.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from realtime.realtime_service import manager
import logging

logger = logging.getLogger("ws")
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/events/{event_id}")
async def websocket_event_channel(event_id: str, websocket: WebSocket):
    """
    WebSocket endpoint — client subscribes to a specific event channel.
    Sends a welcome message with current subscriber count.
    Keeps connection alive until client disconnects.
    """
    await manager.connect(event_id, websocket)
    try:
        # Send initial connection confirmation
        import json
        await websocket.send_text(json.dumps({
            "type": "CONNECTED",
            "event_id": event_id,
            "message": f"Subscribed to real-time updates for event {event_id}",
            "subscribers": manager.get_subscriber_count(event_id)
        }))
        # Keep connection alive — wait for client to disconnect
        while True:
            # We don't expect messages from client, but we must await to detect disconnect
            data = await websocket.receive_text()
            # Optionally handle ping/pong
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        manager.disconnect(event_id, websocket)
        logger.info("Client disconnected from event channel: %s", event_id)
    except Exception as exc:
        logger.error("WebSocket error on channel %s: %s", event_id, exc)
        manager.disconnect(event_id, websocket)
