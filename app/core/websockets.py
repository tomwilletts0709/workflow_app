from collections import defaultdict
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

class WebSocketManager(): 
    def __init__(self): 
        #store all currently connect websockets. defaultdict used to automatically created empty lists
        self.active_connection: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, project_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connection[project_id].append(websocket) 

    def disconnect(self, project_id: int,  websocket: WebSocket):
        connections = self.active_connection[project_id]

        if websocket in connections: 
            connections.remove(websocket)
        
        if not connections: 
            del self.active_connection[project_id]

    #websocket.accept() = backend to accpe the clients websocket upgrade request

    #add a broadcast
    async def broadcast_to_project(self, project_id: int, message: dict[str, Any]): 
        connections = self.active_connection[project_id]

        for connection in connections: 
            await connection.send_json(message)

manager = WebSocketManager() 
websocket_router = APIRouter()

@websocket_router.websocket("/ws/projects/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: int): 
    await manager.connect(project_id, websocket)

    await websocket.send_json({
        "type": "connected", 
        "project_id": project_id,
        "message": f"Subscribed to project: {project_id}"
    })
   
    try: 
        while True: 
            await websocket.receive_text()
    except WebSocketDisconnect: 
        manager.disconnect(project_id, websocket)



        


    