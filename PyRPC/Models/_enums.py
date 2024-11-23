
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
    FUNCTION = "function"
    METHOD = "method"
    STATIC_METHOD = "static method"
    CLASS_METHOD = "class method"
    CLASS = "class"

class MiddleWareStatus(StrEnum):
    """
    中间件的状态
    """
    NORMAL = "normal"
    CONTINUE = "continue"
    WANT_TO_CLOSE = "want to close the connection"