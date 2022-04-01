import redis
import random
import time
import os

queries = [(b'[fin', b'(fio'), (b'[pa', b'(pc'), (b'[see', b'(sef')]

REDIS_HOSTNAME = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

def exec_cmd_with_time():
    try:
        socket = redis.Redis(
            host=REDIS_HOSTNAME, port=REDIS_PORT, password=REDIS_PASSWORD,
            db=REDIS_DB
        )

        latencies = []
        for _ in range (0, 1000):
        
            q = random.choice(queries)
            start_q, end_q = q

            st = time.time()
            result = socket.zrangebylex("word_index", min=start_q, max=end_q, start = 0, num = 10)
            et = time.time()

            print(result)
            latencies.append(et - st)

        print('latency:', (sum(latencies) / 1000) * 1000, 'ms')
    
    except Exception as e:
        print('redis search error ', e)
        os._exit(0)


exec_cmd_with_time()