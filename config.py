 # -*- coding: utf-8 -*-

import os
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/zlbbs?charset=utf8'
# SQLALCHEMY 里面的模型一有变动，那么他都会给我们发送一个信号，没有必要会浪费性能
SQLALCHEMY_TRACK_MODIFICATIONS = True

# session 加密
SECRET_KEY = 'man man lai'

# 将 cms 后台用来保存 user.id 的 key ，提取为一个全局变量
CMS_USER_ID = 'cms_user_id'
FRONT_USER_ID = 'front_user_id'


# 邮箱配置信息
MAIL_SERVER = "SMTP.qq.com"
MAIL_PORT = "587"
MAIL_USE_TLS = True
MAIL_USERNAME = "1010784344@qq.com"
# 并不是上面邮箱用户的密码
MAIL_PASSWORD = "blotkweqnlwpbccj"
MAIL_DEFAULT_SENDER = "1010784344@qq.com"




# 短信验证配置信息
ALIDAYU_APP_KEY = ''
ALIDAYU_APP_SECRET = ' '
ALIDAYU_SIGN_NAME = '仙剑论坛网站'
ALIDAYU_TEMPLATE_CODE = 'SMS_184820719'



# flask_paginate 的相关配置(分页，一页多少个)
PER_PAGE = 10


# celery 的相关配置
CELERY_RESULT_BACKEND = 'redis://@127.0.0.1:6379/0'
CELERY_BROKER_URL = 'redis://@127.0.0.1:6379/0'
