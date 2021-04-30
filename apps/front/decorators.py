# -*- coding: UTF-8 -*-

from flask import session,redirect,url_for,g
import config
from functools import wraps


# 定义登录限制装饰器
def LoginRequired(func):
    @wraps(func)
    def inner(*args,**kwargs):

        # 判断 session 中是否存在某个 key
        # if 'user_id' in session:
        if config.FRONT_USER_ID in session:
            return func(*args,**kwargs)
        else:
            # 使用 url_for 反转 基于调度方法及蓝图的视图函数
            return redirect(url_for('front.signin'))
    return inner




if __name__ == '__main__':
    pass