# -*- coding: utf-8 -*-


import os


DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1/zlbbs?charset=utf8'
# SQLALCHEMY 里面的模型一有变动，那么他都会给我们发送一个信号，没有必要会浪费性能
SQLALCHEMY_TRACK_MODIFICATIONS = True

# session 加密
SECRET_KEY = 'man man lai'

# 将 cms 后台用来保存 user.id 的 key ，提取为一个全局变量
CMS_USER_ID = 'cms_user_id'
FRONT_USER_ID = 'front_user_id'

# flask_paginate 的相关配置(分页，一页多少个)
PER_PAGE = 4

# celery 的相关配置
CELERY_RESULT_BACKEND = 'redis://@127.0.0.1:6379/1'
CELERY_BROKER_URL = 'redis://@127.0.0.1:6379/1'

# 路径配置相关信息
APPS_DIR = os.path.dirname(__file__)
UPLOADED_DIR = os.path.join(APPS_DIR, 'contests')
CONF_INFO = """server {

    listen       80;
    server_name %s.testnginx.com;
    location / {
        proxy_pass   http://%s:%s;
    }
}"""



















