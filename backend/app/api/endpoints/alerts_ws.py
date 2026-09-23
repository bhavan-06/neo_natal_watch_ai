from fastapi import WebSocket, WebSocketDisconnect
from .ws_manager import manager

# This endpoint allows the frontend to establish a WebSocket connection
# and receive real‑time high‑risk alerts broadcast by the inference service.

async def alerts_websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive; we don't expect messages from client.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

