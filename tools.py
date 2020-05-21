import hashlib
import logging
import os


def md5(text):
    m = hashlib.md5()
    m.update(text.encode())
    return m.hexdigest()


def logger(logname):
    log = logging.getLogger(logname)
    log.setLevel(logging.INFO)
    detail = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
    log_dir = os.path.join(os.getcwd(), 'log')
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    handler = logging.FileHandler(filename=os.path.join(log_dir, logname + '.log'), encoding='utf-8')
    handler.setFormatter(detail)
    log.addHandler(handler)
    return log


if __name__ == '__main__':
    log = logger('xiantian')
    log.info("测试")
