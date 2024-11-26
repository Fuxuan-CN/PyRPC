

from abc import ABC, abstractmethod
from typing import Callable

class IRemoteCallable(ABC):

    @abstractmethod
    def __init__(self, name: str) -> None:
        """ 初始化远程调用函数 """
        self.name = name
        self.callitems: dict[str, Callable] = {}

    @abstractmethod
    def call(self, *args, **kwargs) -> object:
        """ 远程调用函数 """
        pass

    @abstractmethod
    def registerCall(self, name: str, item: Callable) -> None:
        """ 注册远程调用函数 """
        pass

    @abstractmethod
    def unregisterCall(self, name: str) -> None:
        """ 注销远程调用函数 """
        pass