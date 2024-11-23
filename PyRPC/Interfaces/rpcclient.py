
from abc import ABC, abstractmethod
from ..Models.datamodels import RpcRequest
from typing import Any

class IRPCClient(ABC):
    @abstractmethod
    def connect(self, host: str, port: int) -> None:
        """ 连接到远程RPC服务器 """

    @abstractmethod
    def IsConnected(self) -> bool:
        """ 是否已连接到远程RPC服务器 """

    @abstractmethod
    def call(self, req: RpcRequest) -> Any:
        """ 调用远程RPC服务,返回结果 """
        pass

    @abstractmethod
    def getAllCallables(self) -> list:
        """ 获取所有可调用的函数信息 """
        pass

    @abstractmethod
    def close(self) -> None:
        """ 关闭连接 """
        pass

    @abstractmethod
    def exceptionBack(self, e: Exception) -> None:
        """ 异常回调 """
        pass

    @abstractmethod
    def ping(self) -> bool:
        """ 测试连接是否正常 """
        pass

    @abstractmethod
    def retry(self, times: int) -> None:
        """ 如果连接失败,重试次数 """
        pass