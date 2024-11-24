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
    server = RPCServer(debug=False)
    server.addCallItem(rpc)
    server.run(("127.0.0.1", 8000))