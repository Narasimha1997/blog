import requests
import time

data = {
    "jsonrpc": "2.0",
    "method": "eth_getBlockByNumber",
    "params": ["0xa0f46a", False],
    "id": 1
}

st = time.time()
response = requests.post("https://rinkeby.infura.io/v3/22b23b601d364f999c0a7cf6deb7bad4", json=data)
et = time.time()

print('time taken: ', et - st, 'seconds')
print('output', response.json())