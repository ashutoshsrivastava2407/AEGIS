"""Real-Time Event WebSocket Stream Router."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from apps.api.realtime import ws_manager
from packages.config import settings

router = APIRouter(prefix="/realtime", tags=["Real-Time Stream"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str = Query(default=settings.DEFAULT_TENANT_ID)
):
    await ws_manager.connect(websocket, tenant_id)
    try:
        while True:
            # Client heartbeat or command listener
            data = await websocket.receive_text()
            # Echo heartbeat ping/pong back
            await websocket.send_json({"type": "HEARTBEAT_ACK", "client_data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, tenant_id)
