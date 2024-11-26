
# PyRPC (Remote Procedure Call)

## 介绍

PyRPC 是一款基于 Python 的远程过程调用（RPC）框架。它可以帮助开发者轻松地实现分布式系统中的服务调用, 该项目基于 Fastapi(Websocket) 实现。 以允许异步调用为核心，通过异步编程模型实现高并发、高性能的 RPC 服务。

## 特性

- 基于 Fastapi(Websocket) 实现，支持 Websocket 长连接，支持异步调用

## 快速开始

### 安装

```bash
pip install pyrpc
```

### 编写服务端

```python
from PyRPC.Server import RPCServer
from PyRPC.Server import RemoteCallable

rpc = RemoteCallable()

@rpc.registerCall
def add(a: int, b: int) -> int:
    return a + b

@rpc.registerCall
def someThing() -> str:
    return "Hello World!"

if __name__ == '__main__':
    server = RPCServer()
    server.addCallItem(rpc)
    server.run("127.0.0.1", 8000)
```

### 编写客户端

```python
from PyRPC.Client import RPCClient

client = RPCClient("localhost", 8000)

result = client("add" , 2, 3)
print(result)
```

### 运行

```bash
python server.py
```

```bash
python client.py
```

### 如果需要异步

```python
from PyRPC.Client import AsyncRPCClient
import asyncio

async def main():
    client = AsyncRPCClient("localhost", 8000)
    result = await client("add" , 2, 3)
    print(result)

if __name__ == '__main__':
    asyncio.run(main())
```

### 如果要添加中间件

```python
from PyRPC.Server import RPCServer
from PyRPC.Server import RemoteCallable
from PyRPC.Server.Security import DefaultRPCAuth

rpc = RemoteCallable()
defaultAuth = DefaultRPCAuth() # 我提供的默认的身份验证中间件

@rpc.registerCall
def add(a: int, b: int) -> int:
    return a + b

@rpc.registerCall
def someThing() -> str:
    return "Hello World!"

if __name__ == '__main__':
    server = RPCServer(debug=False)
    server.addCallItem(rpc)
    server.addMiddleWare(defaultAuth) # add authentication middleware
    server.run("127.0.0.1", 8000)
```
