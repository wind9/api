import requests
import pymysql
import time
import traceback
from config import global_config as config
import tools
import random
import json
from threading import Thread

charge_url = config.get('xt', 'charge_url')
PlatID = config.get('xt', 'PlatID')
API_KEY = config.get('xt', 'API_KEY')
db_host = config.get('xt', 'db_host')
db_host = config.get('xt', 'db_host')
db_port = int(config.get('xt', 'db_port'))
db_user = config.get('xt', 'db_user')
db_password = config.get('xt', 'db_password')
db_name = config.get('xt', 'db_name')
thread_num = int(config.get('xt', 'thread_num'))
log = tools.logger('xt')
redis = tools.get_redis('xt')


def pre_charge(phone, face):
    flag = False
    try:
        con = pymysql.Connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_name)
        cursor = con.cursor()
        month = time.strftime('%Y%m')[2:]
        time_str = time.strftime('%Y%m%d%H%M%S')
        sql = "insert into phonerepository{}(phone,face,tradetime,chgtime,state) values({},{},{},{},0)".format(month, phone, face, time_str, time_str)
        cursor.execute(sql)
        con.commit()
        cursor.close()
        con.close()
        flag = True
    except Exception:
        log.info(traceback.format_exc())
    finally:
        return flag


def charge(phone, face):
    resp = ''
    params = {
        "PlatID": PlatID,
        "NodeOrderID": "a{}{}".format(int(time.time()*1000), random.randint(0, 100)),
        "Phone": phone,
        "Fee": face*100,
        "CallBackUrl": "",
        "TransType": "01",
        "IP": "121.201.16.55",
    }
    sorted_keys = sorted(params.keys())
    value_str= ''
    for k in sorted_keys:
        value_str = value_str + str(params[k])
    sign = tools.md5(value_str + API_KEY)
    params['Sign'] = sign.upper()
    try:
        if pre_charge(phone, face):
            log.info("号码{}面值{}已插入数据库".format(phone, face))
            r = requests.post(charge_url, data=params)
            resp = r.text
    except Exception:
        log.info(traceback.format_exc())
    finally:
        return resp


def result_parse(resp):
    success = False
    try:
        result = json.loads(resp)
        success = result['success']
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
        resp = charge(phone, int(face))
        log.info("线程{}获取{},执行结果{}".format(thread_id, charge_info, resp))
        check_enable(resp)
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
