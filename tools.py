import hashlib
import logging
import os
import json
from config import global_config as config
from redis import StrictRedis, ConnectionPool


def md5(text):
    m = hashlib.md5()
    m.update(text.encode())
    return m.hexdigest()


def logger(logname):
    log = logging.getLogger(logname)
    log.setLevel(logging.INFO)
    detail = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
    log_dir = os.path.join(os.path.dirname(__file__), 'log')
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    handler = logging.FileHandler(filename=os.path.join(log_dir, logname + '.log'), encoding='utf-8')
    handler.setFormatter(detail)
    log.addHandler(handler)
    return log


def get_redis(db_name):
    redis_host = config.get('public', 'redis_host')
    redis_port = config.get('public', 'redis_port')
    redis_password = config.get('public', 'redis_password')
    db = config.get(db_name, 'redis_db_name')
    pool = ConnectionPool(host=redis_host, port=redis_port, password=redis_password, db=db)
    redis = StrictRedis(connection_pool=pool)
    return redis


def init_orders(api_name, order_file):
    redis = get_redis(api_name)
    with open(order_file, 'r') as f:
        for line in f.readlines():
            line = line.strip().split()
            charge_info = {}
            charge_info['phone'] = line[0]
            charge_info['face'] = line[1]
            redis.lpush('order', json.dumps(charge_info))


if __name__ == '__main__':
    order_file_dir = os.path.join(os.path.dirname(__file__), 'conf')
    order_file = os.path.join(order_file_dir, 'phones.txt')
    api_name = os.environ.get('api')
    #api_name = 'bn'
    init_orders(api_name, order_file)
