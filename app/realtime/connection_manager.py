from uuid import uuid4

from fastapi import WebSocket
from pydantic import BaseModel


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept a new websocket connection and return its connection ID.
        """

        await websocket.accept()

        # ------------------------------------------------------------------
        # TODO: Authentication
        #
        # 1. Extract JWT from query params or headers.
        # 2. Validate JWT.
        # 3. Extract user_id.
        # 4. Reject unauthorized users:
        #       await websocket.close(code=1008)
        #       raise Exception("Unauthorized")
        #
        # Store user_id mapping here once authentication is implemented.
        # ------------------------------------------------------------------

        connection_id = str(uuid4())

        self._connections[connection_id] = websocket

        return connection_id

    async def disconnect(self, connection_id: str) -> None:
        websocket = self._connections.pop(connection_id, None)

        if websocket is None:
            return

        try:
            await websocket.close()
        except Exception:
            pass

    async def send(self, connection_id: str, message: BaseModel | dict) -> bool:
        websocket = self._connections.get(connection_id)

        if websocket is None:
            return False

        try:
            if isinstance(message, BaseModel):
                await websocket.send_json(message.model_dump())
            else:
                await websocket.send_json(message)

            return True

        except Exception:
            await self.disconnect(connection_id)
            return False

    async def broadcast(self, message: BaseModel | dict) -> None:
        for connection_id in list(self._connections.keys()):
            await self.send(connection_id, message)

    def get(self, connection_id: str) -> WebSocket | None:
        return self._connections.get(connection_id)

    def is_connected(self, connection_id: str) -> bool:
        return connection_id in self._connections


connection_manager = ConnectionManager()