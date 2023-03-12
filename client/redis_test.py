import socket
import pickle
import sys
import redis

redis = redis.Redis()
#redis.mset({"1": "board", "2":"board"})
print(str(redis.mget("98")))

