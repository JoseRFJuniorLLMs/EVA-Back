# Video Call WebSocket Manager
from typing import Dict, Set
from fastapi import WebSocket
import uuid
import json

class ConnectionManager:
    def __init__(self):
        # atendente_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, atendente_id: str):
        await websocket.accept()
        self.active_connections[atendente_id] = websocket
        print(f"✅ Atendente {atendente_id} conectado via WebSocket")
    
    def disconnect(self, atendente_id: str):
        if atendente_id in self.active_connections:
            del self.active_connections[atendente_id]
            print(f"❌ Atendente {atendente_id} desconectado")
    
    async def send_personal_message(self, message: dict, atendente_id: str):
        if atendente_id in self.active_connections:
            websocket = self.active_connections[atendente_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todos os atendentes online"""
        for atendente_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except:
                print(f"⚠️ Erro ao enviar para atendente {atendente_id}")

# Instância global do gerenciador
manager = ConnectionManager()
