
from abc import ABC, abstractmethod
from fastapi import WebSocket , FastAPI
from ..Models import MiddleWareStatus
from typing import Optional

class IRPCMiddleWare(ABC):
    """ 自定义RPC中间件接口 """

    def __init__(self, app: FastAPI, ws: Optional[WebSocket] = None, sequence: int = 0) -> None:
        self.app = app
        self.ws = ws
        self.sequence = sequence

    @abstractmethod
    async def before(self, *args, **kwargs) -> MiddleWareStatus:
        """ 再处理RPC请求之前的操作 """
        pass

    @abstractmethod
    async def after(self, *args, **kwargs) -> None:
        """ 再处理RPC请求之后的操作 """
        pass

    @abstractmethod
    async def setApp(self, app: FastAPI) -> None:
        """ 设置FastAPI实例 """
        pass

    @abstractmethod
    async def setWebSocket(self, ws: WebSocket) -> None:
        """ 设置WebSocket实例 """
        pass