import requests
import threading
import random
import time
import tools
import traceback
import json
from threading import Thread
from config import global_config as config


log = tools.logger('bn')
agentId = config.get('bn', 'agentId')
businessId = config.get('bn', 'businessId')
tradePwd = config.get('bn', 'tradePwd')
charge_url = config.get('bn', 'charge_url')
appKey = config.get('bn', 'appKey')
thread_num = int(config.get('bn', 'thread_num'))
sleep_time = int(config.get('bn', 'sleep_time'))
redis = tools.get_redis('bn')


def charge(phone, face):
    resp = ''
    param = {
        "agentId": agentId,
        "businessId": businessId,
        "reqStreamId": "fd{}{}".format(str(round(time.time()*1000)), random.randint(100, 1000)),
        "phone": str(phone),
        "face": str(face),
        "tradePwd": tools.md5(tradePwd),
        "timeStamp": time.strftime('%Y%m%d%H%M%S'),
    }
    param2 = sorted(param)
    param['notify'] = ""
    source_str = "".join([param[k] for k in param2]) + appKey
    param['sign'] = tools.md5(source_str)
    try:
        r = requests.get(charge_url, params=param)
        resp = r.text
    except Exception:
        log.info(traceback.format_exc())
    finally:
        return resp


def result_parse(resp):
    success = False
    try:
        result = json.loads(resp)
        if result['status'] in (0, 2):
            success = True
    except Exception as e:
        log.info(traceback.format_exc())
    finally:
        return success


def check_enable(resp):
    if resp and result_parse(resp):
        redis.set('enable', 1)
        redis.set('fail_count', 0)
    else:
        fail_count = int(redis.get('fail_count'))
        redis.set('fail_count', fail_count+1)
        log.info("第{}次提交失败".format(fail_count+1))
        if fail_count + 1 > int(config.get('xt', 'max_fail')):
            log.info("第{}次提交失败,已达最大失败次数,充值暂停".format(fail_count+1))
            redis.set('enable', 0)


def run(thread_id):
    while int(redis.get('enable')) and redis.llen('order') > 0:
        charge_info = json.loads(redis.rpop('order'))
        phone = charge_info['phone']
        face = charge_info['face']
        resp = charge(phone, face)
        log.info("线程{}获取{},执行结果{}".format(thread_id, charge_info, resp))
        check_enable(resp)
        if sleep_time:
            time.sleep(sleep_time)
    log.info("取单暂停")


def main():
    log.info("开始执行...")
    redis.set('enable', 1)
    redis.set('fail_count', 0)
    thread_list = []
    for thread_id in range(thread_num):
        t = Thread(target=run, args=(thread_id,))
        thread_list.append(t)
    for t in thread_list:
        t.setDaemon(True)
        t.start()
        t.join()


if __name__ == '__main__':
    main()
