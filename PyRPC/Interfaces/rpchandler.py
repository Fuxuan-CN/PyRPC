
from abc import ABC, abstractmethod
from ..Models.datamodels import RpcRequest , RpcResponse
from typing import Any , Callable

class IRPCHandler(ABC):

    @abstractmethod
    def __init__(self, call_items: dict = {}) -> None:
        """ 初始化 """
        self.call_items = call_items
        self.name = self.__class__.__name__

    @abstractmethod
    def handle_request(self, request: RpcRequest) -> RpcResponse:
        """ 处理RPC请求 """
        pass

    @abstractmethod
    def _handle(self, request: RpcRequest) -> RpcResponse:
        """ 处理RPC请求 """
        pass

    @abstractmethod
    def call_function(self, func: Callable, *args, **kwargs) -> Any:
        """ 处理函数调用 """
        pass

    @abstractmethod
    def call_method(self, obj: Any, method_name: str, *args, **kwargs) -> Any:
        """ 处理方法调用 """
        pass

    @abstractmethod
    def call_static_method(self, class_name: str, method_name: str, *args, **kwargs) -> Any:
        """ 处理静态方法调用 """
        pass

    @abstractmethod
    def call_class_method(self, class_name: str, method_name: str, *args, **kwargs) -> Any:
        """ 处理类方法调用 """
        pass

    @abstractmethod
    def get_class(self, class_name: str) -> Any:
        """ 获取类实例 """
        pass

    @abstractmethod
    def exception_returned(self, exception: Exception) -> RpcResponse:
        """ 处理调用异常 """
        pass