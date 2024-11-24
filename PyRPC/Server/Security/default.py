
from ...Models import  AuthRegisterPayload , IdentityClientCard , MiddleWareStatus
from ...Interfaces import IRPCMiddleWare
from fastapi import WebSocket , FastAPI
import time
from datetime import timedelta
from typing import Any
import jwt
from ...Utils.logger import get_logger
from pydantic_core import ValidationError
import json

class DefaultRPCAuth(IRPCMiddleWare):
    """ 默认RPC认证类 """
    def __init__(self, sequence: int = 1) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.sequence = sequence

    async def authenticate(self, payload: IdentityClientCard) -> bool:
        """ 验证客户端请求 """
        try:
            jwt.decode(payload.token, "secret", algorithms=["HS256"])
        except jwt.exceptions.InvalidTokenError:
            self.logger.info(f"Invalid authentication token: {payload.token}")
            return False
        except jwt.exceptions.ExpiredSignatureError:
            self.logger.info(f"Expired authentication token: {payload.token}")
            return False
        
    async def registerUser(self, payload: AuthRegisterPayload) -> IdentityClientCard:
        """ 注册用户 """
        try:
            expire = time.time() + timedelta(weeks=1).total_seconds()
            authPayload = jwt.encode({"username": payload.username, "password": payload.password, "exp": expire}, "secret", algorithm="HS256")
            return IdentityClientCard(serverAllowed=True, token=authPayload)
        except Exception as e:
            self.logger.error(f"Failed to register user: {type(e).__name__} - {str(e)}")
            return IdentityClientCard(serverAllowed=False, token=None)
        
    async def before(self,app: FastAPI, ws: WebSocket, *args, **kwargs) -> MiddleWareStatus:
        """ 客户端连接时调用 """
        try:
            authInfo = await ws.receive_json()
            authDict: dict = json.loads(authInfo)
            mode = authDict.get("mode", "")
            if mode == "register":
                self.logger.trace(f"Received register request: {authDict}")
                req = AuthRegisterPayload(**authDict)
                card = await self.registerUser(req)
                await self.ws.send_json(card.model_dump(mode="json"))
                return MiddleWareStatus.NORMAL
            elif mode == "auth":
                self.logger.trace(f"Received authentication request: {authDict}")
                req = IdentityClientCard(**authDict)
                if await self.authenticate(req) is False:
                    self.logger.info("Client authentication failed")
                    await self.ws.send_json({"status": "failed", "message": "Unauthorized access"})
                    return MiddleWareStatus.WANT_TO_CLOSE
                else:
                    self.logger.info("Client authentication succeeded")
                    await self.ws.send_json({"status": "success", "message": "Authentication succeeded"})
                    return MiddleWareStatus.NORMAL
            else:
                self.logger.info(f"Invalid authentication mode: {mode}")
                await self.ws.send_json({"status": "failed", "message": "Invalid authentication mode"})
                return MiddleWareStatus.WANT_TO_CLOSE
        except ValidationError:
            self.logger.info("Invalid authentication request")
            await self.ws.send_json({"status": "failed", "message": "Invalid authentication request"})
            return MiddleWareStatus.WANT_TO_CLOSE
        
    async def after(self,app: FastAPI, ws: WebSocket, *args, **kwargs) -> None:
        return
    
    async def __call__(self, app: FastAPI, ws: WebSocket, *args, **kwargs) -> Any:
        """ 调用中间件 """
        status = await self.before(app, ws, *args, **kwargs)
        return status
        