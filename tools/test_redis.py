from redis import StrictRedis, ConnectionPool
from config import config
import time


redis_host = config.get('public', 'redis_host')
redis_port = config.get('public', 'redis_port')
redis_password = config.get('public', 'redis_password')
start_time = time.time()
pool = ConnectionPool(host=redis_host, port=redis_port, password=redis_password, db=0)
redis = StrictRedis(connection_pool=pool)

