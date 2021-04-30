# -*- coding: utf-8 -*-
from flask import session,redirect,url_for,g
import config
from functools import wraps


# 定义登录限制装饰器
def LoginRequired(func):
    @wraps(func)
    def inner(*args,**kwargs):

        # 判断 session 中是否存在某个 key
        # if 'user_id' in session:
        if config.CMS_USER_ID in session:
            return func(*args,**kwargs)
        else:
            # 使用 url_for 反转 基于调度方法及蓝图的视图函数
            return redirect(url_for('cms.login'))
    return inner


# 视图函数权限限制装饰器
# 如果没有权限就返回到 cms 首页
def permission_required(permission):
    def outter(func):
        @wraps(func)
        def inner(*args,**kwargs):
            user = g.cms_user
            if user.has_permission(permission):
                return func(*args,**kwargs)
            else:
                return redirect(url_for('cms.index'))
        return inner
    return outter











