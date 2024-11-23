from abc import ABC, abstractmethod
from .rpchandler import IRPCHandler
from .rpccallitem import IRemoteCallable
from ..Models import CallableCheckResponse

class IRPCServer(ABC):

    @abstractmethod
    def run(self, host: str, port: int) -> None:
        """ 启动RPC服务 """
        pass

    @abstractmethod
    def setHandler(self, handler: IRPCHandler) -> None:
        """ 注册RPC处理器 """
        pass

    @abstractmethod
    def removeHandler(self, handler: IRPCHandler) -> None:
        """ 注销RPC处理器 """
        pass

    @abstractmethod
    def getAllCallInfos(self) -> list[CallableCheckResponse]:
        """ 获取所有可远程调用的对象信息 """
        pass

    @abstractmethod
    def addCallItem(self, item: IRemoteCallable) -> None:
        """ 注册可远程调用的对象 """
        pass

    @abstractmethod
    def handle(self) -> None:
        """ 处理RPC请求 """
        pass

    @abstractmethod
    def _beforeHandle(self) -> None:
        """ 处理请求前的准备工作 """
        pass

    @abstractmethod
    def _afterHandle(self) -> None:
        """ 处理请求后的清理工作 """
        pass