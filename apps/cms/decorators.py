# -*- coding: utf-8 -*-


from flask import session, redirect, url_for
from functools import wraps

import config


# 定义登录限制装饰器
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):

        # 判断 session 中是否存在某个 key
        # if 'user_id' in session:
        if config.CMS_USER_ID in session:
            return func(*args, **kwargs)
        else:
            # 使用 url_for 反转 基于调度方法及蓝图的视图函数
            return redirect(url_for('cms.login'))
    return inner













