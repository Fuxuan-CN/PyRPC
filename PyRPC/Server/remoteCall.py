
from ..Interfaces import IRemoteCallable
from typing import Callable
from functools import wraps

class RemoteCallable(IRemoteCallable):
    """ 远程调用类 """
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.callitems = {}
        super().__init__(name=self.name)

    def registerCall(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        self.callitems[func.__name__] = wrapper
        return wrapper

    def call(self, name: str, *args, **kwargs) -> object:
        if name in self.callitems:
            return self.callitems[name](*args, **kwargs)
        else:
            raise AttributeError(f"Attribute {name} not found in {self.__class__.__name__}")

    def __getattr__(self, name: str) -> Callable:
        if name in self.callitems:
            return self.callitems[name]
        else:
            raise AttributeError(f"Attribute {name} not found in {self.__class__.__name__}")
        
    def unregisterCall(self, name: str) -> None:
        if name in self.callitems:
            del self.callitems[name]

    def get_all_callables(self) -> list[Callable]:
        return list(self.callitems.values())