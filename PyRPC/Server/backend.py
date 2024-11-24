
from ..Interfaces import IRPCServer , IRPCHandler , IRemoteCallable , IRPCMiddleWare
from ..Models import RpcRequest , CallableCheckResponse
from ..Utils.logger import get_logger
from .Handlers import DefaultHandler
from starlette.websockets import WebSocketState
from ..Models import MiddleWareStatus
import uvicorn
import inspect
import asyncio
from typing import Callable
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocketDisconnect

class RPCServer(IRPCServer):
    def __init__(self, debug: bool = False):
        self.handler: IRPCHandler = None
        self.app = FastAPI()
        self.logger = get_logger(self.__class__.__name__)
        self.middlewares: list[IRPCMiddleWare] = []
        self.registed_callables: dict[str, IRemoteCallable] = {}
        self.clients = []
        self.infoCache = None
        self.debug = debug
        self.headers = {
            "User-Agent": "Python RPC Server / backend / FastAPI"
        }
        self._configure_cors()

    async def isConnected(self, ws: WebSocket) -> bool:
        return ws.application_state == WebSocketState.CONNECTED and ws.client_state == WebSocketState.CONNECTED
    
    async def closeConnection(self, ws: WebSocket, code: int = 1000, reason: str = "Normal closure"):
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                self.logger.debug(f"Closing WebSocket connection: {ws.client}")
                await ws.close(code=code, reason=reason)
            else:
                self.logger.debug(f"WebSocket connection already closed: {ws.client}")
        except Exception as e:
            # 处理关闭连接时可能发生的任何异常
            self.logger.exception(f"Error while closing connection: {e}")
        finally:
            if ws in self.clients:
                self.clients.remove(ws)

    async def openConnection(self, ws: WebSocket) -> WebSocket:
        if await self.isConnected(ws):
            self.logger.info(f"WebSocket connection already exists: {ws.client}")
            return ws
        else:
            await ws.accept()
            self.clients.append(ws)
            self.logger.info(f"WebSocket connection opened: {ws.client}")
            return ws

    def _configure_cors(self) -> None:
        """ 允许跨域请求 """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

    def addMiddleWare(self, middleware: IRPCMiddleWare) -> None:
        """ 添加中间件 """
        self.middlewares.append(middleware)
        self.middlewares.sort(key=lambda x: x.sequence)  # 根据优先级排序
        self.logger.info(f"MiddleWare {middleware.__class__.__name__} added.")

    def setHandler(self, handler: IRPCHandler) -> None:
        self.handler = handler
        self.logger.info(f"Handler {handler.__class__.__name__} setered to server")

    def removeHandler(self, name: str) -> None:
        if name is self.handler.name:
            self.handler = None
            self.logger.info(f"Handler {name} removed from server")

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        if self.handler is None:
            self.logger.warning("No handler set, server will use a default handler")
            self.handler = DefaultHandler(self._parseCall())

        self.logger.info(f"Starting server on ws://{host}:{port})")
        self.handle() # 在启动之前先注册路由
        if self.debug:
            self.logger.warning("Debug mode is on, server will not be started in production environment")
            uvicorn.run(self.app, host=host, port=port, log_level="debug")
        else:
            uvicorn.run(self.app, host=host, port=port, log_level="critical")
        self.logger.info("Server stopped")

    def addCallItem(self, item: IRemoteCallable) -> None:
        self.logger.debug(f"Adding callItem {item.name}, callable: {item.callitems}")
        if item.name in self.registed_callables:
            self.logger.warning(f"CallItem {item.name} already exists, overwriting")
        self.registed_callables[item.name] = item

    def _parseCall(self) -> dict[str, Callable]:
        calls = {}
        for _, item in self.registed_callables.items():
            for call_name , call_able in item.callitems.items():
                calls[call_name] = call_able
        self.logger.debug(f"Calls: {calls}")
        return calls
    
    def getAllCallInfos(self) -> list[CallableCheckResponse]:
        self.logger.debug("Getting all call infos")
        result: list[CallableCheckResponse] = []
        for _, item in self.registed_callables.items():
            for callName, callAble in item.callitems.items():
                parameters = inspect.signature(callAble).parameters
                pType = callAble.__annotations__
                pInfo = [{"name": k, "type": pType.get(k, "Any").__name__} for k in parameters.keys()]
                pDictInfo = {k: pType.get(k, "Any").__name__ for k in parameters.keys()}
                result.append(CallableCheckResponse(callName=callName, requireArgs=tuple(pInfo), requireKwargs=pDictInfo, returnType=pType.get("return", "Any").__name__))
        return result
    
    async def _beforeHandle(self, ws: WebSocket, *args, **kwargs) -> tuple[WebSocket, MiddleWareStatus]:
        self.logger.trace(f"Before handle, client: {ws.client}")
        status = None
        """ 在处理请求之前调用 """
        if len(self.middlewares) == 0:
            self.logger.debug("No middlewares, accept connection directly")
            return ws , MiddleWareStatus.NORMAL
        for middleware in self.middlewares:
            self.logger.trace(f"Middleware {middleware.__class__.__name__} before handle")
            status = await middleware.before(app=self.app, ws=ws, *args, **kwargs)
        return ws , status
        
    async def _afterHandle(self, ws: WebSocket, status: str, *args, **kwargs) -> None:
        self.logger.trace(f"After handle, client: {ws.client}")
        """ 在处理请求之后调用 """
        if len(self.middlewares) == 0:
            await self._after(ws, status)
        for middleware in self.middlewares:
            self.logger.trace(f"Middleware {middleware.__class__.__name__} after handle")
            await middleware.after(app=self.app, ws=ws, *args, **kwargs)
        await self._after(ws, status)

    async def _after(self, ws: WebSocket, status: str) -> None:
        if status == MiddleWareStatus.NORMAL or status == MiddleWareStatus.CONTINUE:
            return await self.closeConnection(ws, reason="invoke completed")
        elif status == MiddleWareStatus.WANT_TO_CLOSE:
            self.logger.info("The websocket connection is closed by the middlewares")
            return await self.closeConnection(ws, reason="the middleware want to close the connection")
        else:
            self.logger.info(f"Client {ws.client} disconnected with error")
            return await self.closeConnection(ws, reason="invoke completed with error")

    async def _handle(self, websocket: WebSocket, middlewareStatus: MiddleWareStatus, *args, **kwargs) -> tuple[WebSocket, str]:
        """ 处理请求 """
        if middlewareStatus == MiddleWareStatus.WANT_TO_CLOSE:
            self.logger.info(f"the middleware want to close the connection with client: {websocket.client}")
            return websocket, MiddleWareStatus.WANT_TO_CLOSE
        
        self.clients.append(websocket)
        self.logger.info(f"New client connected: {websocket.client}")
        try:
            while True:
                data = await websocket.receive_json()
                to_rpc_request = RpcRequest.model_validate_json(data)
                self.logger.debug(f"Received request: {to_rpc_request.model_dump(mode='json')}")
                response = self.handler.handle_request(to_rpc_request)
                await websocket.send_json(response.model_dump(mode="json"))
        except WebSocketDisconnect: # 如果是正常断开连接，则正常退出
            status = MiddleWareStatus.NORMAL
        except Exception as e: # 如果是其他异常，则记录日志，关闭连接
            self.logger.exception(f"Error while handling request: {e}")
            status = "Error exit"
        return websocket, status

    def handle(self) -> None:
        @self.app.get("/rpc/callables")
        async def get_callables():
            if not self.infoCache:
                self.infoCache = await asyncio.to_thread(self.getAllCallInfos)
            return self.infoCache
        
        @self.app.websocket("/ws/rpc")
        async def websocket_endpoint(websocket: WebSocket):
            opened_ws = await self.openConnection(websocket)
            before_ws , middlewareStatus = await self._beforeHandle(opened_ws) 
            handled_ws, status = await self._handle(before_ws, middlewareStatus)
            await self._afterHandle(handled_ws, status)