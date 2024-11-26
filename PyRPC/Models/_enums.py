
from enum import StrEnum


class CallType(StrEnum):
    """
    调用的时候指定调用类型
    """
    WITH_NO_ARGS = "with no args"
    WITH_ARGS = "with args"
    WITH_KWARGS = "with kwargs"
    WITH_KEY_VALUE_PAIRS = "with key=value pairs"

class MethodType(StrEnum):
    """
    调用的方法类型
    """
    CALLABLE: str = "callable"

class MiddleWareStatus(StrEnum):
    """
    中间件的状态
    """
    NORMAL = "normal"
    CONTINUE = "continue"
    WANT_TO_CLOSE = "want to close the connection"