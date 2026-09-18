"""Real-Time Event WebSocket & Connection Manager."""

import json
from typing import Dict, List, Set
from fastapi import WebSocket
from packages.observability import logger


class ConnectionManager:
    def __init__(self) -> None:
        # Maps tenant_id -> Set of active WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str) -> None:
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
        logger.info(f"WebSocket connected for tenant {tenant_id}")

    def disconnect(self, websocket: WebSocket, tenant_id: str) -> None:
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
        logger.info(f"WebSocket disconnected for tenant {tenant_id}")

    async def broadcast_to_tenant(self, tenant_id: str, message: dict) -> None:
        if tenant_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[tenant_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Error broadcasting to WebSocket: {e}")
                    disconnected.append(connection)

            for conn in disconnected:
                self.disconnect(conn, tenant_id)


ws_manager = ConnectionManager()
