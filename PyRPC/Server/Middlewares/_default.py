
from ...Interfaces import IRPCMiddleWare
from fastapi import FastAPI, WebSocket

class ExampleMiddleware(IRPCMiddleWare):
    def __init__(self, app: FastAPI = None, ws: WebSocket = None) -> None:
        self.app = app
        self.ws = ws

    async def before(self) -> None:
        return await self.ws.accept()

    async def after(self) -> None:
        return

    async def setApp(self, app: FastAPI) -> None:
        self.app = app

    async def setWebSocket(self, ws: WebSocket) -> None:
        self.ws = ws