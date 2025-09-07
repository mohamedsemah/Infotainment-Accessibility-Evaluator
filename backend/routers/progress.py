from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, upload_id: str):
        await websocket.accept()
        if upload_id not in self.active_connections:
            self.active_connections[upload_id] = []
        self.active_connections[upload_id].append(websocket)
        logger.info(f"WebSocket connected for upload {upload_id}")
    
    def disconnect(self, websocket: WebSocket, upload_id: str):
        if upload_id in self.active_connections:
            self.active_connections[upload_id].remove(websocket)
            if not self.active_connections[upload_id]:
                del self.active_connections[upload_id]
        logger.info(f"WebSocket disconnected for upload {upload_id}")
    
    async def send_progress(self, upload_id: str, message: dict):
        if upload_id in self.active_connections:
            for connection in self.active_connections[upload_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send progress message: {e}")
                    # Remove failed connection
                    self.active_connections[upload_id].remove(connection)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all active connections"""
        for upload_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to broadcast message: {e}")

manager = ConnectionManager()

@router.websocket("/progress")
async def websocket_progress(
    websocket: WebSocket,
    upload_id: str = Query(..., description="Upload ID to track progress for")
):
    """
    WebSocket endpoint for real-time progress updates
    """
    await manager.connect(websocket, upload_id)
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
            elif message.get("type") == "subscribe":
                # Client wants to subscribe to specific events
                events = message.get("events", [])
                logger.info(f"Client subscribed to events: {events}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, upload_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, upload_id)

# Progress tracking functions
async def send_upload_progress(upload_id: str, progress: float, status: str, message: str = ""):
    """Send upload progress update"""
    await manager.send_progress(upload_id, {
        "type": "upload_progress",
        "upload_id": upload_id,
        "progress": progress,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

async def send_analysis_progress(upload_id: str, progress: float, status: str, current_step: str, message: str = ""):
    """Send analysis progress update"""
    await manager.send_progress(upload_id, {
        "type": "analysis_progress",
        "upload_id": upload_id,
        "progress": progress,
        "status": status,
        "current_step": current_step,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

async def send_agent_progress(upload_id: str, agent_id: str, agent_name: str, progress: float, status: str, message: str = ""):
    """Send agent execution progress update"""
    await manager.send_progress(upload_id, {
        "type": "agent_progress",
        "upload_id": upload_id,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "progress": progress,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

async def send_clustering_progress(upload_id: str, progress: float, status: str, clusters_count: int, message: str = ""):
    """Send clustering progress update"""
    await manager.send_progress(upload_id, {
        "type": "clustering_progress",
        "upload_id": upload_id,
        "progress": progress,
        "status": status,
        "clusters_count": clusters_count,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

async def send_patching_progress(upload_id: str, progress: float, status: str, patches_count: int, message: str = ""):
    """Send patching progress update"""
    await manager.send_progress(upload_id, {
        "type": "patching_progress",
        "upload_id": upload_id,
        "progress": progress,
        "status": status,
        "patches_count": patches_count,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

async def send_sandbox_progress(upload_id: str, progress: float, status: str, message: str = ""):
    """Send sandbox progress update"""
    await manager.send_progress(upload_id, {
        "type": "sandbox_progress",
        "upload_id": upload_id,
        "progress": progress,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

async def send_completion(upload_id: str, status: str, message: str = "", results: dict = None):
    """Send completion notification"""
    await manager.send_progress(upload_id, {
        "type": "completion",
        "upload_id": upload_id,
        "status": status,
        "message": message,
        "results": results or {},
        "timestamp": datetime.now().isoformat()
    })

async def send_error(upload_id: str, error_type: str, error_message: str, details: dict = None):
    """Send error notification"""
    await manager.send_progress(upload_id, {
        "type": "error",
        "upload_id": upload_id,
        "error_type": error_type,
        "error_message": error_message,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    })

# Export progress functions for use in other modules
__all__ = [
    "send_upload_progress",
    "send_analysis_progress", 
    "send_agent_progress",
    "send_clustering_progress",
    "send_patching_progress",
    "send_sandbox_progress",
    "send_completion",
    "send_error"
]
