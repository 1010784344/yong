# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_mail import Mail
from utils.alidayu import AlidayuAPI

# 用来发送邮件
mail = Mail()

# 用来获取短信验证 码
alidayu = AlidayuAPI()

