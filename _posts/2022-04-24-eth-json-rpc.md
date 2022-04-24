---
title: Concurrent and Batch JSON-RPC calls on Ethereum Blockchain 
published: true
---

Ethereum has a very well defined set of methods that can be used to interact with the blockchain from external systems (probably from our current Web 2.0 systems). Ethereum exposes these functionalities over [JSON-RPC 2.0](https://www.jsonrpc.org/specification) protocol. In brief, JSON-RPC is a light-weight data interchange protocol built on top of application layer protocols like HTTP and Web Sockets. Using JSON-RPC we specify the method we want to invoke and the list of parameters to be passed, the method is then executed by the Ethereum's JSON-RPC server to which we have connected and returns the output as JSON which can be consumed by the caller. When compared to [gRPC](https://grpc.io/) and other known RPC protocols JSON-RPC is relatively simple and uses plain text JSON which is more readable and easily understandable. We can see the list of methods provided by Ethereum blockchain via JSON-RPC protocol [here](](https://eth.wiki/json-rpc/API)). 

Here is a sample JSON-RPC payload to get the information of a block on the ethereum blockchain by it's number:
```json
{
    "jsonrpc": "2.0",
    "method": "eth_getBlockByNumber",
    "params": ["0xa0f46a", true],
    "id": 1
}
``` 
We are calling the method `eth_getBlockByNumber` by passing the block number `10548330` (or `0xa0f46a` in hex) and the boolean value which specifies whether to output full transaction output or just the transaction hashes. Similar to `eth_getBlockByNumber` there are many methods with their own parameter requirements. 

We can make HTTP POST request to the JSON-RPC node by submitting the above JSON payload. Here is an example of how it can be done with python:

```python
import requests
import time

data = {
    "jsonrpc": "2.0",
    "method": "eth_getBlockByNumber",
    "params": ["0xa0f46a", False],
    "id": 1             # id is just a number for keeping track of the request on client-side
}

st = time.time()
response = requests.post("https://rinkeby.infura.io/v3/22b23b601d364f999c0a7cf6deb7bad4", json=data)
et = time.time()

print('time taken: ', et - st, 'seconds')
print('output', response.json())
```
Output:
```
time taken:  0.8727474212646484 seconds
output {'jsonrpc': '2.0', 'id': 1, 'result': {'baseFeePerGas': '0xb', 'difficulty': '0x2', 'extraData': '0xd683010a11846765746886676f312e3138856c696e75780000000000000000005484b299653ddb09be6dfcaf019b2d387564cd4eedc3c7a670837fca65feaab251a0a95cb1e14fbb6b7e00680d0318eb03522b7ae5ba0d6623991439b8a257a001', 'gasLimit': '0x1c9c380', 'gasUsed': '0x5c35eb', 'hash': '0x7b5bc82fae1cb1a695e4bea1da405b8b3e953d30ce63167571bb0eba538ec028', 'logsBloom': '0x0828404000000b0000044801a110a92050208002624440000c03384090200008805042185008200410000c0000001a1231408804080cbc0004000a1011363040360000000080206a41a000080022602108060204946410228604805486100000022041002200c003000412101800481080c0002000000601840100d1000802001000a30c06c100100248b00000008040c50000010240010880000044406030380200000008020408488440000580200a3504006408c000188808214e0000120048200d0228044001000200810020404408000680810800140b00110a0480e20122343c0aa290400020ac000081050891001963b0482223400040580980002403', 'miner': '0x0000000000000000000000000000000000000000', 'mixHash': '0x0000000000000000000000000000000000000000000000000000000000000000', 'nonce': '0x0000000000000000', 'number': '0xa0f46a', 'parentHash': '0xc70e1a85c2d7e865ffe71ae1e8c78539ad2d9268b469abfa06554c2c8ac71205', 'receiptsRoot': '0xdec4ee3b890662d88f6635d5ffa05c0aba25731701224735192d076d6fad019c', 'sha3Uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347', 'size': '0x61c5', 'stateRoot': '0x9af1e2dee823147a30eff0e66c4498addbc90550aacbd65f184b1fcf13a3a162', 'timestamp': '0x62628dd8', 'totalDifficulty': '0x10a83f5', 'transactions': ['0x8fc61b71557e445c832d0c7ac0d9a19dac13b4cf92a40dd59fa27b1faf3a5781', '0x1598f0db451fd6503bcba735dbf91b785a7aeee4fba37cc83d75508ce242c354', '0xe07bcd936979f10378af2610dc5209656662754c05a501404bd757564f9b7ca8', '0xb579c46b357a344e339bbe695cbeb7d8e80cbf3a48e359c3ac68ec937c2b41bd', '0x2020771e9c08ccae2770393c0c652d5161ae6d276bf5b2509f7e38d5d008a182', '0xca805dfe9fc1e2a13cfbf0cfc6fb3be29e12d60e29deb68140293559a4388384', '0x44b67a281d17279f0cd005b7101bfbbba3300463b5a5d3123eca32e06f0b5810', '0xd990f40743486fba6ce0d187516ad49c6cd92d7520ce80447606aea69a86c841', '0x11849bac6d3d20090d8a708cd59aaaef3412a63c4c3f1b26dacef5cc999c5038', '0xfe60a91ac75fe31a8df0acc425c931c8ecaf2692519bb365bf8501def85f5dda', '0x4f4715aa0f544b8c1a2d6229dbe683d2814081d8a39609cfcb12451d3c87bb7d', '0x97e439cb02f1e8bf4f7db89e96407e67bbbc75253bf82ebb2aa3e10304376c30', '0x129021ec232712f422089a4fa2bfb7f0c5a58e19ea1bfa8e0c37ed380942e589', '0xca429b804e925e4e28a0132a4ac42b7bd19583193cbaf5da7d8ce956cae4ef5c', '0x12fc6f6277452657d730b5518016ef84281cf5961d3ed4d1a38439a6df64dca9', '0x7e733c1e4f9ce0e0f5a3d7d455ef870588844687f980386f788c378940eaa911', '0x50c86aa5756a3d8bc0282668a9e58378b1297f0be4c7a77aa26ef38aa69698fc', '0xd49611a95ba2eed4426a3942e38d3ff043eba86e171542be04b3a3a550d318d3', '0x0a92aa7a60f1d3b97d86f9665cece2bf85248ac7d5e732547cf33ee17e387f15', '0xa91e155c129b4d8449635aee1c1cbbbde7a7f8108cc45c05aa030fc34b7b16e8', '0xf7a900e2a50400b4bbcb4f6c51256cf9125347c171b107d4a86ff7d9c852b59f', '0x090add0f1d441c97b54f40d8ec54575102f66307fa03e330d44cee6bb6a1b69c', '0xad8869d19e73ee2f57e4f0d3697a58bf902ad03cea3c1c7b7cf40c9e621ffaeb', '0x022d10b70c903220475bab28d412153a47514abed92288bfbe98224dc8e7128c', '0x367cec4698f401f166864b485d21c9aedfd26f8d28d512cd15bcd7ddb4f7e86d', '0x6ba8af557b1931d5d0e095f4ca04ccc31e9a96c03596b59264c7d894814fafef', '0x1de3719a13d7141ac9db10668b29921df6dce2d3b8ee5c6307b9d19fa9b67e8a', '0x13928fe6d5af70bff7773ecf2c11528a7abcba6b8898bdd72bb68bc6d9bed414', '0x7784245cf801dfcb7c2cbd92abcee9b78e0e4fc02b617d8a2884a9f9ecff878b', '0x6a926356ea4d1198605be6cddab626b9fc5fb3f8934bcb7f0785b42fcdba1866', '0x4046f17200f5c2a316f042d5393bd555f2d05d97615122089a34972f424e676b', '0x81a4036a5e4723d93cd058b63768545444e6b29abee1cb2d9b87b05ee2310927', '0x30a1ec3718a279aec9dc10a1ff3214a2c193e89797152f7e8ab92e6728d02580', '0xb18d695cba61e4d021505bdf001c565458bd25e0f291be34311ac03dc00334e8', '0xca4d12a4b7c51ef30be26fb7489be9c6cfed25603d41f2503b38a98e342ffbfb', '0x86ca6b8b86fc54d017b116e69f188baf3d2c60fbdbb4e4617380a436a1fce767', '0x117b48440bbbdd89edf5776df2e5fed599e4ef69e5bd1405a9cac3b8264faede'], 'transactionsRoot': '0xed1e6d5dd38173c6f6fe0ec25c056a71d3e0ca9c39d1c891b63af8993526c5f5', 'uncles': []}}
```
This is the most simple way to get started with making JSON-RPC calls. We directly made raw RPC calls on the blockchain, instead of that we can also use full-fledged client libraries avaibale in many languages. For example [web3.py](https://web3py.readthedocs.io/en/stable/) is a python implementation of high-level ethereum JSON-RPC calls.

From the above output we came to know that an average web3 call via JSON-RPC takes 900ms (this depends on many factors and is different for different RPC methods) to get data of one block. Imagine we need to query hundreds of such blocks, in that case we will be wasting lot of time (approximately 90s) in our case. To mitigate this issue, we can either go for concurrent JSON-RPC calls using asynchronous networking capabilities or follow [JSON-RPC batch specification](https://sajya.github.io/docs/batch/).

In the following sections we will create a simple client package that can be used to make concurrent and batch JSON-RPC calls.

### Preparing for concurrent and batch calls:
In the above example we used [requests](https://docs.python-requests.org/en/latest/) module to make JSON-RPC calls over HTTP, this is fine but the blocking nature of synchronous HTTP requests becomes a bottleneck when we want to scale for thousands of RPC calls. So instead of `requests` module, we will use [aiohttp](https://docs.aiohttp.org/en/stable/) which is built around python's [asyncio](https://docs.python.org/3/library/asyncio.html) capabilities. We will first create a class that abstracts away all `aiohttp` stuff and provides a cleaner API to use as a python module.

```python
class EthAioAPI:

    def __init__(self):
        pass

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *err):
        await self.session.close()
        self.session = None
```
This class has `__aenter__` and `__aexit__` methods which will be called upon entry and exit of `asyncio` scope respectively, we will use these methods to manage our session object which will be created and closed automatically as we enter and leave the scope. 

We want to pass in the URL to which we want to connect in the constructor. Our API should accept N tasks and execute them together as batch or concurrently. To accommodate these features, we modify the above code as follows:
```python
class EthAioAPI:

    def __init__(self, url: str, max_tasks=100):
        self.url = url
        self.current_tasks = []
        self.current_id = 0
        self.max_tasks = max_tasks

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *err):
        await self.session.close()
        self.session = None
    
    def push_task(self, task: dict):

        if self.current_id >= self.max_tasks:
            raise Exception("maximum tasks exceeded")

        payload = {
            "jsonrpc": "2.0",
            "method": task["method"],
            "params": task["params"],
            "id": self.current_id
        }

        self.current_tasks.append(payload)
        self.current_id += 1
    
    def set_max_tasks(self, n: int):
        self.max_tasks = n 
```
We added few members in the constructor, the `url` stores the URL string of the gateway RPC node to which we want to connect, `current_tasks` holds the list of tasks submitted via `push_task` method and `current_id` keeps track of a number that is just incremented every time to assign a new ID for the task. `max_tasks` represents how many tasks we can execute together, as you can see a check is made in `push_task` method before allowing the task to be added to the list, we can use `set_max_tasks` anytime to change this limit. Now that we have necessary structures to hold our tasks, we can go ahead and build functions to execute these tasks together - we can do this in two ways, i.e either concurrently or as a batch. 

### Making concurrent (asynchronous) requests:
`aiohttp` provides us capabilities to execute tasks concurrently, using the asynchronous system calls provided by the operating system, in other words, unlike `requests` module, here each call is executed in a non-blocking way without blocking our main thread, thus we can schedule N requests at a time to run in background and `await` for results. To achieve this, we create an asynchronous function called `tasklet` which makes a single JSON-RPC call without blocking. To run N concurrent requests we call `tasklet` N times and they are executed concurrently. Here is our `tasklet` function:
```python
async def tasklet(id: int, url: str, session: aiohttp.ClientSession, payload: dict) -> dict:
        try:
            response = await session.post(
                url, json=payload,
                headers={"Content-Type": "application/json"}
            )
            json_resp = await response.json()
            json_resp['success'] = True
            return json_resp
        except Exception as e:
            return {"success": False, "exception": e, "id": id}
```
The `tasklet` function makes a web3 call, if there is a failure returns the failure information or it returns the response dictionary by adding a new entry `"success": True` to the response. Finally we create a class method `exec_tasks_async` which calls a `tasklet` for each task submitted using `push_task` method.
```python
async def exec_tasks_async(self):
        fns = []
        for id, task_payload in enumerate(self.current_tasks):
            task_fn = EthAioAPI.tasklet(
                id, self.url, self.session, task_payload)
            fns.append(task_fn)

        outputs = await asyncio.gather(*fns, return_exceptions=True)

        self.current_tasks.clear()
        self.current_id = 0
        return outputs
```
This method pushes `tasklet` function for each task to the event loop and calls them together using `asyncio.gather()` and gathers the outputs, the outputs are returned in the same order in which the tasks are submitted. Once we receive the outputs we reset our task list so new tasks can be submitted next time. 

This method allows us to call N JSON-RPCs at a time without waiting for individual calls to complete. However, in this approach we are using the resources on the client side to open N concurrent sockets and also we end up making lot of Web3 calls which might sometimes get rate-limited. 

### Making batch request:
As per JSON-RPC spec, we can send a list of RPC calls at a time and expect the results for all the calls from the server at once. This is left to the implementors of the JSON-RPC server, they can choose to implement this functionality or choose to ignore it, however [few Ethereum JSON-RPC implementations](https://eth.wiki/json-rpc/API) supports batched calls. We will now add `exec_tasks_batch` class method to add Batch calls support in our client:
```python
async def exec_tasks_batch(self):
        try:
            response = await self.session.post(
                self.url, json=self.current_tasks, headers={
                    "Content-Type": "application/json"}
            )

            json_resp = await response.json()
            self.current_tasks.clear()
            self.current_id = 0

            return json_resp

        except Exception as e:
            raise e
```
As you can see, this method just submits the entire task list as it is and the output we get is a list of responses for each call in the list.

In this method, we will be using the resources of the RPC server to execute N tasks at a time for us, in client side we need only one socket and we open only one connection. (Here we are depending on the server. So make sure the RPC server you are connecting to supports this functionality).

### Final code:
```python
import asyncio
import aiohttp


class EthAioAPI:

    def __init__(self, url: str, max_tasks=100):
        self.url = url
        self.current_tasks = []
        self.current_id = 0
        self.max_tasks = max_tasks

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *err):
        await self.session.close()
        self.session = None

    async def tasklet(
        id: int,
        url: str,
        session: aiohttp.ClientSession,
        payload: dict
    ) -> dict:

        try:
            response = await session.post(
                url, json=payload,
                headers={"Content-Type": "application/json"}
            )

            json_resp = await response.json()
            json_resp['success'] = True

            return json_resp

        except Exception as e:
            return {"success": False, "exception": e, "id": id}

    def push_task(self, task: dict):

        if self.current_id >= self.max_tasks:
            raise Exception("maximum tasks exceeded")

        payload = {
            "jsonrpc": "2.0",
            "method": task["method"],
            "params": task["params"],
            "id": self.current_id
        }

        self.current_tasks.append(payload)
        self.current_id += 1

    async def exec_tasks_batch(self):
        try:
            response = await self.session.post(
                self.url, json=self.current_tasks, headers={
                    "Content-Type": "application/json"}
            )

            json_resp = await response.json()
            self.current_tasks.clear()
            self.current_id = 0

            return json_resp

        except Exception as e:
            raise e

    async def exec_tasks_async(self):
        fns = []
        for id, task_payload in enumerate(self.current_tasks):
            task_fn = EthAioAPI.tasklet(
                id, self.url, self.session, task_payload)
            fns.append(task_fn)

        outputs = await asyncio.gather(*fns, return_exceptions=True)

        self.current_tasks.clear()
        self.current_id = 0
        return outputs

    def set_max_tasks(self, n: int):
        self.max_tasks = n
```

We can create a folder called `aio_eth` and copy this code as `__init__.py` which allows us to import `aio_eth` and use it as a module.

### Let's test!
We can use the class we built in the previous sections to test and verify the functionalities, First let's execute a sample JSON-RPC call N times concurrently and check how it works:
```python
import asyncio
# our module
import aio_eth
import time

URL = "https://rinkeby.infura.io/v3/b6fe23ef7add48d18d33c9bf41d5ad0c"

async def query_blocks():
    async with aio_eth.EthAioAPI(URL, max_tasks=100) as api:
        for i in range(10553978, 10553978 + 70):
            api.push_task({
                "method": "eth_getBlockByNumber",
                "params": [
                    hex(i), True
                ]
            })

        st = time.time()
        _ = await api.exec_tasks_async()
        et = time.time()
        print('time taken: ', et - st, ' seconds')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(query_blocks())
``` 
Output:
```
time taken:  1.5487761497497559  seconds
```
So it takes us around 1.5 seconds to execute 70 RPC calls asynchronously. Now let's try batch JSON-RPC call:
```python
import asyncio
import aio_eth
import time

URL = "https://rinkeby.infura.io/v3/b6fe23ef7add48d18d33c9bf41d5ad0c"

async def query_blocks():
    async with aio_eth.EthAioAPI(URL, max_tasks=100) as api:
        for i in range(10553978, 10553978 + 70):
            api.push_task({
                "method": "eth_getBlockByNumber",
                "params": [
                    hex(i), True
                ]
            })

        st = time.time()
        _ = await api.exec_tasks_batch()
        et = time.time()
        print('time taken: ', et - st, ' seconds')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(query_blocks())
```
Output:
```
time taken:  3.698002576828003  seconds
```
To achieve same result using Batch JSON-RPC call it takes us 3.7 seconds, which is twice as that of concurrent JSON-RPC calls. However, this varies across different methods and amount of data the server returns over the network. To achieve the same in sequential way, it would take us around 65-70 seconds, thus using either concurrency or batch mode we can save lot of time and hence we can scale our client to make lot of JSON-RPC calls in less time.

### Getting aio_eth package from PyPi
I have published the above code as a PyPi package so people can download and use it. The PyPi package can be found [here](https://pypi.org/project/aio-eth/). We can also use `pip` to install this package:
```
pip install aio-eth
```
The package is open source and can be found on [Github](https://github.com/Narasimha1997/aio-eth).