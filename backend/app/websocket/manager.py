from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
from datetime import datetime
from ..schemas.websocket import WebSocketMessage, NotificationMessage


logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Store user sessions
        self.user_sessions: Dict[WebSocket, str] = {}
        # Store room memberships (for project-based updates)
        self.room_memberships: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a user to WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.user_sessions[websocket] = user_id
        
        logger.info(f"User {user_id} connected to WebSocket")
        
        # Send connection confirmation
        await self.send_personal_message(user_id, {
            "type": "connection_confirmed",
            "data": {"message": "Connected to real-time updates"}
        })
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a user from WebSocket"""
        if websocket in self.user_sessions:
            user_id = self.user_sessions[websocket]
            
            # Remove from active connections
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from user sessions
            del self.user_sessions[websocket]
            
            # Remove from all rooms
            for room_id, members in self.room_memberships.items():
                members.discard(user_id)
            
            logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            websocket_message = WebSocketMessage(
                type=message["type"],
                data=message["data"]
            )
            
            # Send to all connections for this user
            disconnected_connections = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(websocket_message.json())
                except:
                    disconnected_connections.append(websocket)
            
            # Clean up disconnected connections
            for websocket in disconnected_connections:
                self.disconnect(websocket)
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in a room"""
        if room_id in self.room_memberships:
            websocket_message = WebSocketMessage(
                type=message["type"],
                data=message["data"]
            )
            
            for user_id in self.room_memberships[room_id]:
                if exclude_user and user_id == exclude_user:
                    continue
                
                if user_id in self.active_connections:
                    disconnected_connections = []
                    for websocket in self.active_connections[user_id]:
                        try:
                            await websocket.send_text(websocket_message.json())
                        except:
                            disconnected_connections.append(websocket)
                    
                    # Clean up disconnected connections
                    for websocket in disconnected_connections:
                        self.disconnect(websocket)
    
    async def join_room(self, user_id: str, room_id: str):
        """Add user to a room"""
        if room_id not in self.room_memberships:
            self.room_memberships[room_id] = set()
        
        self.room_memberships[room_id].add(user_id)
        
        # Notify user they joined the room
        await self.send_personal_message(user_id, {
            "type": "room_joined",
            "data": {"room_id": room_id}
        })
    
    async def leave_room(self, user_id: str, room_id: str):
        """Remove user from a room"""
        if room_id in self.room_memberships:
            self.room_memberships[room_id].discard(user_id)
            
            # Clean up empty rooms
            if not self.room_memberships[room_id]:
                del self.room_memberships[room_id]
        
        # Notify user they left the room
        await self.send_personal_message(user_id, {
            "type": "room_left",
            "data": {"room_id": room_id}
        })
    
    async def broadcast_test_execution_update(self, execution_data: dict):
        """Broadcast test execution updates"""
        message = {
            "type": "test_execution_update",
            "data": execution_data
        }
        
        # Broadcast to project room
        project_id = execution_data.get("project_id")
        if project_id:
            await self.broadcast_to_room(f"project_{project_id}", message)
    
    async def broadcast_comment_update(self, comment_data: dict):
        """Broadcast new comment updates"""
        message = {
            "type": "comment_update",
            "data": comment_data
        }
        
        # Broadcast to test case watchers
        test_case_id = comment_data.get("test_case_id")
        if test_case_id:
            await self.broadcast_to_room(f"testcase_{test_case_id}", message)
    
    async def broadcast_dashboard_update(self, dashboard_data: dict):
        """Broadcast dashboard updates"""
        message = {
            "type": "dashboard_update",
            "data": dashboard_data
        }
        
        # Broadcast to all connected users
        for user_id in self.active_connections:
            await self.send_personal_message(user_id, message)
    
    async def send_notification(self, user_id: str, notification: NotificationMessage):
        """Send notification to specific user"""
        message = {
            "type": "notification",
            "data": notification.dict()
        }
        
        await self.send_personal_message(user_id, message)
    
    def get_connected_users(self) -> List[str]:
        """Get list of currently connected users"""
        return list(self.active_connections.keys())
    
    def get_room_members(self, room_id: str) -> List[str]:
        """Get list of users in a specific room"""
        return list(self.room_memberships.get(room_id, set()))

# Global WebSocket manager instance
websocket_manager = WebSocketManager()