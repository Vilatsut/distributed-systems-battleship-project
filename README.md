# distributed-systems-battleship-project
Course project for distributed systems course


Requirements:
1. Redis: https://redis.io/docs/getting-started/installation/install-redis-on-windows/
2. Python
 
To start the program manually:
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

via docker:
docker run -it --network="host" holappaj/lb:1
docker run -it --network="host" holappaj/chat:1
docker run -it --network="host" holappaj/game:1

start the client normally:
python ./client/client.py

