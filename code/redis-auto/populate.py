import requests
import redis
import os
from itertools import permutations

REDIS_HOSTNAME = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

MAX_PERM = 200

def get_all_prefixes(word):
    perms = [word[0:i] for i in range(0, len(word) + 1)]
    perms[-1] = perms[-1] + "*"
    return perms

def get_word_list():
    try:
        data = requests.get("https://raw.githubusercontent.com/dwyl/english-words/master/words.txt")
        all_words =  data.text.split("\n")[:-1]
        print('got ', len(all_words), 'words')

        all_words_records = {}
        for word in all_words:
            perms = get_all_prefixes(word)
            all_words_records.update({ perm: 0 for perm in perms })
        
        return all_words_records
    except Exception as e:
        print('Error getting word list', e)
        os._exit(-1)

def create_redis_words_index(index_data):
    try:
        socket = redis.Redis(
            host=REDIS_HOSTNAME, port=REDIS_PORT, password=REDIS_PASSWORD,
            db=REDIS_DB
        )

        # avoid socket write error by writing 100k elements at a time
        idx = 0
        temp_dict = {}
        for k, v in index_data.items():
            idx +=1
            temp_dict[k] = v
            if idx == 100 * 1000:
                print('inserting', idx, 'words')
                socket.zadd("word_index", temp_dict)
                idx = 0
                temp_dict.clear()
        else:
            print('inserting', idx, 'words')
            socket.zadd("word_index", temp_dict)

    except Exception as e:
        print('Redis index build error: ', e)
        os._exit(-1)

if __name__ == "__main__":
    index = get_word_list()
    print('Creating index of', len(index), 'entries')
    create_redis_words_index(index)
