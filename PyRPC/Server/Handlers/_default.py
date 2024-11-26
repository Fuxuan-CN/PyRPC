from ...Interfaces import IRPCHandler
from ...Models import RpcRequest, RpcResponse, CallType
from ...Utils.logger import getLogger
from ...Utils import ExtractException
from typing import Any , Callable

class DefaultHandler(IRPCHandler):
    """ 默认处理器 """
    def __init__(self, call_items: dict = {}) -> None:
        self.call_items = call_items # 存储已注册的函数或方法
        self.name = self.__class__.__name__
        self.logger = getLogger(self.__class__.__name__)
        if not self.call_items:
            self.logger.warning("No call items found, please register call items first.")

    def handleRequest(self, request: RpcRequest) -> None:
        """ 处理请求 """
        return self._handle(request)

    def _handle(self, request: RpcRequest) -> RpcResponse:
        """ 处理请求 """
        try:
            if request.callbody.callitem in self.call_items:
                if request.callType == CallType.WITH_NO_ARGS:
                    result = self.callCanCallable(self.call_items[request.callbody.callitem])
                elif request.callType == CallType.WITH_ARGS:
                    result = self.callCanCallable(self.call_items[request.callbody.callitem], *request.callbody.args)
                elif request.callType == CallType.WITH_KWARGS:
                    result = self.callCanCallable(self.call_items[request.callbody.callitem], **request.callbody.kwargs)
                elif request.callType == CallType.WITH_KEY_VALUE_PAIRS:
                    result = self.callCanCallable(self.call_items[request.callbody.callitem], *request.callbody.args, **request.callbody.kwargs)
                else:
                    raise ValueError(f"Invalid callType: {request.callType}")
            else:
                raise ValueError(f"Call item not found: {request.callbody.callitem}")
            self.logger.success("Request handled successfully. no errors detected.")
            return RpcResponse(result=result, error=None, is_error=False)
        except Exception as e:
            self.logger.info("request handling successful, but an error occurred.")
            return self.exceptionReturn(e, False)

    def callCanCallable(self, func: Callable, *args, **kwargs) -> Any:
        """ 处理函数调用 """
        self.logger.info(f"Calling function: {func.__name__}, with args: {args}, kwargs: {kwargs}")
        return func(*args, **kwargs)

    def exceptionReturn(self, exception: Exception, log_error: bool = True) -> None:
        """ 返回异常信息 """
        error = fr"Exception Current: {type(exception).__name__}: {exception}"
        stack = ExtractException(type(exception), exception, exception.__traceback__)
        error += f"\n{stack}"
        if log_error:
            self.logger.error(error) # 记录日志
        return RpcResponse(result=None, error=error, IsError=True)