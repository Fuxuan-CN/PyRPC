from PyRPC.Client import RPCClient

with RPCClient("localhost", 8000) as client:
    try:
        result = client("add", 2, 3)
        print(result)
    except Exception as e:
        print(e)
