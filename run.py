from xt import api as xt
from rt import api as rt
from fl import api as fl
from bn import api as bn
from bx import api as bx
import os


if __name__ == '__main__':
    api_name = os.environ.get('api')
    if api_name == 'xt':
        xt.main()
    elif api_name == 'rt':
        rt.main()
    elif api_name == 'fl':
        fl.main()
    elif api_name == 'bn':
        bn.main()
    elif api_name == 'bx':
        bx.main()
    else:
        print("当前执行的api:{}不存在".format(api_name))
