import socket
import pickle
import sys
import redis

redis = redis.Redis()
#redis.mset({"1": "board", "2":"board"})
print(redis.mget("2"))
