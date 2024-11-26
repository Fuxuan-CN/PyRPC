
from ..Models import RpcRequest, CallType, MethodType, CallBody , RpcResponse , AuthRegisterPayload , IdentityClientCard
from ..Interfaces import IRPCClient
from ..Utils import ExtractException
import websocket
import asyncio
import json
import requests
from .exceptions import RPCConnectionError

class RPCClient(IRPCClient):
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.ws = None
        self.connected = False
        self.connect(host, port)

    def connect(self, host: str, port: int) -> None:
        """ 连接到 RPC 服务器 """
        try:
            self.ws = websocket.create_connection(f"ws://{host}:{port}/ws/rpc")
            self.connected = True
            print("Connected to RPC server")
        except websocket.WebSocketException as e:
            print(f"Connection failed: {e}")
            self.connected = False

    def registerUser(self, payload: AuthRegisterPayload) -> IdentityClientCard:
        """ 发送注册请求 """
        if not self.IsConnected():
            raise RPCConnectionError("Not connected to the RPC server")
        self.ws.send(json.dumps(payload.model_dump_json()))
        resp = self.ws.recv()
        card = IdentityClientCard(**json.loads(resp))
        return card
    
    def authenticate(self, payload: IdentityClientCard) -> dict:
        """ 发送身份验证请求 """
        result = {}
        if not self.IsConnected():
            raise RPCConnectionError("Not connected to the RPC server")
        self.ws.send(json.dumps(payload.model_dump_json()))
        resp = self.ws.recv()
        result = json.loads(resp)
        return result

    def getAllCallables(self) -> list:
        """ 获取 RPC 所有可调用服务 """
        if not self.IsConnected():
            raise RPCConnectionError("Not connected to the RPC server")
        
        Infos = requests.get("http://127.0.0.1:8000/rpc/callables/", headers={"User-Agent": "Python-RPC-Client"})
        return Infos.json()

    def _buildRequest(self, callItem: str, methodType: MethodType, callType: CallType, *args, **kwargs) -> RpcRequest:
        """ 构建 RPC 请求 """
        callBody = CallBody(callitem=callItem, args=args, kwargs=kwargs)
        req = RpcRequest(callType=callType, methodType=methodType, callbody=callBody)
        return req

    def IsConnected(self) -> bool:
        """ 检测是否连接到 RPC 服务器 """
        return self.connected and self.ws.sock is not None

    def _call(self, req: RpcRequest) -> RpcResponse:
        """ 调用 RPC 服务的内部方法 """
        if not self.IsConnected():
            raise RPCConnectionError("Not connected to the RPC server")
        
        requestDump = json.dumps(req.model_dump_json())
        self.ws.send(requestDump)
        response = self.ws.recv()
        dictResponse = json.loads(response)
        rpcResponse = RpcResponse(**dictResponse)
        if rpcResponse.IsError:
            self.exceptionBack(rpcResponse.error)
        return rpcResponse
    
    def call(self, call_item: str, method_type: MethodType, call_type: CallType, *args, **kwargs) -> RpcResponse:
        """ 调用 RPC 服务 """
        req = self._buildRequest(call_item, method_type, call_type, *args, **kwargs)
        return self._call(req)

    def close(self, status: int = 1000, reason: str = "") -> None:
        """ 关闭 RPC 连接 """
        if self.ws:
            self.ws.close(status=status, reason=bytes(reason, "utf-8"))
            self.connected = False
            print("Connection closed")

    def exceptionBack(self, e: Exception | str) -> None:
        """ 处理 RPC 异常 """
        if isinstance(e, str):
            err_info = "Call successed but got an error: \n"
            err_info += e
            print(err_info)
            return
        else:
            err_info = ExtractException(type(e), e, e.__traceback__)
            print(err_info)

    def ping(self) -> bool:
        """ 心跳检测 """
        # Implement ping logic to test the connection
        try:
            self.ws.ping()
            return True
        except websocket.WebSocketException:
            return False

    def retry(self, times: int) -> None:
        """ 重试机制 """
        # Implement retry logic to reconnect to the server
        for attempt in range(times):
            if self.connect("127.0.0.1", 8000):
                print(f"Reconnected on attempt {attempt + 1}")
                break

    def __call__(self, item: str, *args, **kwargs) -> RpcResponse:
        """ 简化调用 RPC 服务 """
        if args:
            return self.call(item, MethodType.CALLABLE, CallType.WITH_ARGS, *args, **kwargs)
        elif kwargs:
            return self.call(item, MethodType.CALLABLE, CallType.WITH_KWARGS, **kwargs)
        elif args and kwargs:
            return self.call(item, MethodType.CALLABLE, CallType.WITH_KEY_VALUE_PAIRS, *args, **kwargs)
        else:
            return self.call(item, MethodType.CALLABLE, CallType.WITH_NO_ARGS)
        
    def __enter__(self) -> "RPCClient":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if (exc_type is not None) and (exc_val is not None) and (exc_tb is not None):
            err_stack = ExtractException(exc_type, exc_val, exc_tb)
            self.exceptionBack(err_stack)
        self.close(1000, "RPC client wants to close the connection.")

class AsyncRPCClient(RPCClient):
    """ 异步 RPC 客户端 """
    def __init__(self, host = "127.0.0.1", port = 8000):
        super().__init__(host, port)

    async def call(self, call_item: str, method_type: MethodType, call_type: CallType, *args, **kwargs) -> RpcResponse:
        """ 异步调用 RPC 服务 """
        result = await asyncio.to_thread(self._call, self._build_request(call_item, method_type, call_type, *args, **kwargs))
        return result
    
    async def getAllCallables(self) -> list:
        """ 异步获取 RPC 所有可调用服务 """
        result = await asyncio.to_thread(
        requests.get, 
        "http://127.0.0.1:8000/rpc/callables/", 
        headers={"User-Agent": "Python-Async-RPC-Client"}).json()
        return result
    
    async def ping(self) -> bool:
        """ 异步心跳检测 """
        result = await asyncio.to_thread(self.ws.ping)
        return result
    
    async def retry(self, times: int) -> None:
        """ 异步重试机制 """
        for attempt in range(times):
            if await asyncio.to_thread(self.connect, "127.0.0.1", 8000):
                print(f"Reconnected on attempt {attempt + 1}")
                break

    async def __call__(self, item: str, *args, **kwargs) -> RpcResponse:
        """ 异步简化调用 RPC 服务 """
        if args:
            return await self.call(item, MethodType.CALLABLE, CallType.WITH_ARGS, *args, **kwargs)
        elif kwargs:
            return await self.call(item, MethodType.CALLABLE, CallType.WITH_KWARGS, **kwargs)
        elif args and kwargs:
            return await self.call(item, MethodType.CALLABLE, CallType.WITH_KEY_VALUE_PAIRS, *args, **kwargs)
        else:
            return await self.call(item, MethodType.CALLABLE, CallType.WITH_NO_ARGS)
    
    async def __aenter__(self) -> "AsyncRPCClient":
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if (exc_type is not None) and (exc_val is not None) and (exc_tb is not None):
            err_stack = ExtractException(exc_type, exc_val, exc_tb)
            self.exceptionBack(err_stack)
        self.close(1000, "Async RPC client wants to close the connection.")