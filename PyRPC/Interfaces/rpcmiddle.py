
from abc import ABC, abstractmethod
from fastapi import WebSocket , FastAPI
from ..Models import MiddleWareStatus
from typing import Optional , Any

class IRPCMiddleWare(ABC):
    """ 自定义RPC中间件接口 """

    def __init__(self, sequence: int = 0) -> None:
        self.sequence = sequence

    @abstractmethod
    async def before(self,app: FastAPI, ws: Optional[WebSocket] = None, *args, **kwargs) -> tuple[str, MiddleWareStatus]:
        """ 再处理RPC请求之前的操作 """
        pass

    @abstractmethod
    async def after(self,app: FastAPI, ws: Optional[WebSocket] = None, *args, **kwargs) -> None:
        """ 再处理RPC请求之后的操作 """
        pass

    async def __call__(self, app: FastAPI, ws: Optional[WebSocket] = None, *args, **kwargs) -> Any:
        """ 允许更直观的调用中间件 """
        pass