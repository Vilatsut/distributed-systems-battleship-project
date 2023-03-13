# distributed-systems-battleship-project
Course project for distributed systems course


Requirements:
1. Redis: https://redis.io/docs/getting-started/installation/install-redis-on-windows/
2. Python
 
To start the program manually (WINDOWS):
1. open CMD (as administrator)
2. clone the repository
3. cd distributed-systems-battleship-project
4. pip install -r requirements.txt
5. python ./loadbalancer/loadbalancer.py
6. python ./gameserver/game_server.py
7. python ./gameserver/game_server.py
8. python ./gameserver/game_server.py
9. python ./chatserver/chatserver.py
10. python ./client/client.py

## To build with Docker.

1. docker build -t <user_name>/loadbalancer:1.0 .

2. cd distributed-systems-battleship-project/chatserver

3. docker build -t <user_name>/chatserver:1.0 .

4. cd distributed-systems-battleship-project/gameserver

5. docker build -t <user_name>/gameserver:1.0 .

### Then run with Docker

docker run -it --network="host" <user_name>/loadbalancer:1.0

docker run -it --network="host" <user_name>/chatserver:1.0

docker run -it --network="host" <user_name>/gameserver:1.0

### Then create two clients

cd distributed-systems-battleship-project
python3 client/client.py
python3 client/client.py
