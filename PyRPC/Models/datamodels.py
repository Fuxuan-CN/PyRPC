from pydantic import BaseModel
from ._enums import CallType, MethodType

class RpcProtocol(BaseModel):
    version: str = '1.0'  # 协议版本

class CallBody(BaseModel):
    callitem: str # 调用的函数名或方法名
    args: tuple = ()  # 请求的参数
    kwargs: dict = {}  # 请求的关键字参数

class RpcRequest(BaseModel):
    protocol: RpcProtocol = RpcProtocol(version='1.0')  # 请求协议版本
    callType: CallType  # 请求类型
    callbody: CallBody  # 调用请求体
    methodType: MethodType  # 请求的方法类型
    
    
class RpcResponse(BaseModel):
    protocol: RpcProtocol = RpcProtocol(version='1.0')  # 响应协议版本
    result: object  # 响应结果
    error: str | None = ''  # 错误信息
    IsError: bool = False  # 是否有错误

class CallableCheckResponse(BaseModel):
    requireArgs: tuple  # 要求的参数
    requireKwargs: dict  # 要求的关键字参数
    callName: str  # 调用的函数名或方法名
    returnType: str  # 返回值类型

class AuthRegisterPayload(BaseModel):
    """ 请求注册的载荷 """
    username: str  # 用户名
    password: str  # 密码
    mode: str = 'register'  # 注册模式，默认为register

class IdentityClientCard(BaseModel):
    serverAllowed: bool  # 服务器是否允许客户端通过身份验证
    token: str | None # 客户端UUID
    mode: str = 'auth'  # 身份验证模式，默认为auth