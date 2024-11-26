
from abc import ABC, abstractmethod
from ..Models.datamodels import RpcRequest , RpcResponse
from typing import Any , Callable

class IRPCHandler(ABC):

    def __init__(self, call_items: dict = {}) -> None:
        """ 初始化 """
        pass

    @abstractmethod
    def handleRequest(self, request: RpcRequest) -> RpcResponse:
        """ 处理RPC请求 """
        pass

    @abstractmethod
    def _handle(self, request: RpcRequest) -> RpcResponse:
        """ 处理RPC请求 """
        pass

    @abstractmethod
    def callCanCallable(self, func: Callable, *args, **kwargs) -> Any:
        """ 处理函数调用 """
        pass

    @abstractmethod
    def exceptionReturn(self, exception: Exception) -> RpcResponse:
        """ 处理调用异常 """
        pass