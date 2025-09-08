"""
Progress router for real-time WebSocket updates during analysis.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from typing import Dict, List, Any, Optional
import json
import asyncio
import logging
from datetime import datetime

from models.schemas import ProgressEvent

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections for progress updates."""
    
    def __init__(self):
        # Dictionary to store active connections by upload_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Dictionary to store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, upload_id: str):
        """Accept a WebSocket connection and add it to the active connections."""
        await websocket.accept()
        
        if upload_id not in self.active_connections:
            self.active_connections[upload_id] = []
        
        self.active_connections[upload_id].append(websocket)
        self.connection_metadata[websocket] = {
            'upload_id': upload_id,
            'connected_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        logger.info(f"WebSocket connected for upload {upload_id}")
        
        # Send initial connection confirmation
        await self.send_personal_message({
            'type': 'connection_established',
            'upload_id': upload_id,
            'timestamp': datetime.now().isoformat(),
            'message': 'Connected to progress updates'
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from active connections."""
        if websocket in self.connection_metadata:
            upload_id = self.connection_metadata[websocket]['upload_id']
            
            if upload_id in self.active_connections:
                self.active_connections[upload_id].remove(websocket)
                if not self.active_connections[upload_id]:
                    del self.active_connections[upload_id]
            
            del self.connection_metadata[websocket]
            logger.info(f"WebSocket disconnected for upload {upload_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]['last_activity'] = datetime.now()
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def send_progress_update(self, upload_id: str, progress_event: ProgressEvent):
        """Send progress update to all connections for a specific upload."""
        if upload_id not in self.active_connections:
            return
        
        message = {
            'type': 'progress_update',
            'upload_id': upload_id,
            'event_type': progress_event.event_type,
            'agent_name': progress_event.agent_name,
            'progress': progress_event.progress,
            'message': progress_event.message,
            'timestamp': progress_event.timestamp.isoformat(),
            'metadata': progress_event.metadata
        }
        
        # Send to all connections for this upload
        connections_to_remove = []
        for websocket in self.active_connections[upload_id]:
            try:
                await websocket.send_text(json.dumps(message))
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]['last_activity'] = datetime.now()
            except Exception as e:
                logger.error(f"Error sending progress update: {e}")
                connections_to_remove.append(websocket)
        
        # Remove failed connections
        for websocket in connections_to_remove:
            self.disconnect(websocket)
    
    async def send_broadcast_message(self, message: dict):
        """Send a message to all active connections."""
        for upload_id, connections in self.active_connections.items():
            for websocket in connections:
                await self.send_personal_message(message, websocket)
    
    def get_connection_count(self, upload_id: str) -> int:
        """Get the number of active connections for an upload."""
        return len(self.active_connections.get(upload_id, []))
    
    def get_all_connections(self) -> Dict[str, int]:
        """Get connection count for all uploads."""
        return {upload_id: len(connections) for upload_id, connections in self.active_connections.items()}

# Global connection manager instance
manager = ConnectionManager()

@router.websocket("/progress")
async def progress_websocket(websocket: WebSocket, upload_id: str = Query(...)):
    """WebSocket endpoint for real-time progress updates."""
    await manager.connect(websocket, upload_id)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                # Handle different message types from client
                if message.get('type') == 'ping':
                    await manager.send_personal_message({
                        'type': 'pong',
                        'timestamp': datetime.now().isoformat()
                    }, websocket)
                elif message.get('type') == 'subscribe':
                    # Client wants to subscribe to specific events
                    await manager.send_personal_message({
                        'type': 'subscription_confirmed',
                        'events': message.get('events', []),
                        'timestamp': datetime.now().isoformat()
                    }, websocket)
                elif message.get('type') == 'unsubscribe':
                    # Client wants to unsubscribe from events
                    await manager.send_personal_message({
                        'type': 'unsubscription_confirmed',
                        'timestamp': datetime.now().isoformat()
                    }, websocket)
            except asyncio.TimeoutError:
                # Send keepalive ping
                await manager.send_personal_message({
                    'type': 'keepalive',
                    'timestamp': datetime.now().isoformat()
                }, websocket)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally for upload {upload_id}")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for upload {upload_id}: {e}")
        manager.disconnect(websocket)

@router.post("/progress/{upload_id}/send")
async def send_progress_update(
    upload_id: str,
    progress_event: ProgressEvent
):
    """Send a progress update to all connected clients for an upload."""
    try:
        await manager.send_progress_update(upload_id, progress_event)
        return {"message": "Progress update sent successfully"}
    except Exception as e:
        logger.error(f"Error sending progress update: {e}")
        raise HTTPException(status_code=500, detail="Failed to send progress update")

@router.get("/progress/{upload_id}/connections")
async def get_connection_info(upload_id: str):
    """Get information about active connections for an upload."""
    try:
        connection_count = manager.get_connection_count(upload_id)
        return {
            "upload_id": upload_id,
            "active_connections": connection_count,
            "status": "active" if connection_count > 0 else "inactive"
        }
    except Exception as e:
        logger.error(f"Error getting connection info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connection info")

@router.get("/progress/connections")
async def get_all_connections():
    """Get information about all active connections."""
    try:
        connections = manager.get_all_connections()
        return {
            "total_uploads": len(connections),
            "total_connections": sum(connections.values()),
            "connections_by_upload": connections
        }
    except Exception as e:
        logger.error(f"Error getting all connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connection info")

@router.post("/progress/{upload_id}/broadcast")
async def broadcast_message(upload_id: str, message: dict):
    """Broadcast a custom message to all connections for an upload."""
    try:
        broadcast_message = {
            'type': 'broadcast',
            'upload_id': upload_id,
            'timestamp': datetime.now().isoformat(),
            **message
        }
        
        if upload_id in manager.active_connections:
            for websocket in manager.active_connections[upload_id]:
                await manager.send_personal_message(broadcast_message, websocket)
        
        return {"message": "Broadcast sent successfully"}
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")

# Utility functions for other modules to use
async def send_agent_start(upload_id: str, agent_name: str, message: str = None):
    """Send agent start event."""
    event = ProgressEvent(
        event_type="agent_start",
        upload_id=upload_id,
        agent_name=agent_name,
        progress=0.0,
        message=message or f"Starting {agent_name}",
        metadata={"agent": agent_name, "status": "starting"}
    )
    await manager.send_progress_update(upload_id, event)

async def send_agent_progress(upload_id: str, agent_name: str, progress: float, message: str = None):
    """Send agent progress update."""
    event = ProgressEvent(
        event_type="agent_progress",
        upload_id=upload_id,
        agent_name=agent_name,
        progress=progress,
        message=message or f"{agent_name} progress: {progress:.1%}",
        metadata={"agent": agent_name, "progress": progress}
    )
    await manager.send_progress_update(upload_id, event)

async def send_agent_complete(upload_id: str, agent_name: str, message: str = None):
    """Send agent completion event."""
    event = ProgressEvent(
        event_type="agent_complete",
        upload_id=upload_id,
        agent_name=agent_name,
        progress=1.0,
        message=message or f"Completed {agent_name}",
        metadata={"agent": agent_name, "status": "completed"}
    )
    await manager.send_progress_update(upload_id, event)

async def send_agent_error(upload_id: str, agent_name: str, error_message: str):
    """Send agent error event."""
    event = ProgressEvent(
        event_type="agent_error",
        upload_id=upload_id,
        agent_name=agent_name,
        progress=0.0,
        message=f"Error in {agent_name}: {error_message}",
        metadata={"agent": agent_name, "status": "error", "error": error_message}
    )
    await manager.send_progress_update(upload_id, event)

async def send_analysis_start(upload_id: str, message: str = "Starting analysis"):
    """Send analysis start event."""
    event = ProgressEvent(
        event_type="analysis_start",
        upload_id=upload_id,
        progress=0.0,
        message=message,
        metadata={"status": "starting"}
    )
    await manager.send_progress_update(upload_id, event)

async def send_analysis_complete(upload_id: str, message: str = "Analysis completed"):
    """Send analysis completion event."""
    event = ProgressEvent(
        event_type="analysis_complete",
        upload_id=upload_id,
        progress=1.0,
        message=message,
        metadata={"status": "completed"}
    )
    await manager.send_progress_update(upload_id, event)

async def send_clustering_start(upload_id: str, message: str = "Starting clustering"):
    """Send clustering start event."""
    event = ProgressEvent(
        event_type="clustering_start",
        upload_id=upload_id,
        progress=0.0,
        message=message,
        metadata={"status": "starting"}
    )
    await manager.send_progress_update(upload_id, event)

async def send_clustering_complete(upload_id: str, message: str = "Clustering completed"):
    """Send clustering completion event."""
    event = ProgressEvent(
        event_type="clustering_complete",
        upload_id=upload_id,
        progress=1.0,
        message=message,
        metadata={"status": "completed"}
    )
    await manager.send_progress_update(upload_id, event)

async def send_patch_generation_start(upload_id: str, message: str = "Generating patches"):
    """Send patch generation start event."""
    event = ProgressEvent(
        event_type="patch_generation_start",
        upload_id=upload_id,
        progress=0.0,
        message=message,
        metadata={"status": "starting"}
    )
    await manager.send_progress_update(upload_id, event)

async def send_patch_generation_complete(upload_id: str, message: str = "Patch generation completed"):
    """Send patch generation completion event."""
    event = ProgressEvent(
        event_type="patch_generation_complete",
        upload_id=upload_id,
        progress=1.0,
        message=message,
        metadata={"status": "completed"}
    )
    await manager.send_progress_update(upload_id, event)