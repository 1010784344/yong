# -*- coding: utf-8 -*-
from exts import db,mail,alidayu
from flask import Flask

from flask_wtf import CSRFProtect

from apps.cms.views import cms_bp
from apps.common.views import common_bp
from apps.front.views import front_bp
from apps.ueditor.ueditor import bp as ued_bp


import config

app = Flask(__name__)

# 引入配置文件
app.config.from_object(config)

# 注册 sqlalchemy 到 app 里面
db.init_app(app)

# 注册邮箱对象 到 app 里面
mail.init_app(app)
#  注册短信验证码 到 app 里面
alidayu.init_app(app)


# csrf 保护
CSRFProtect(app)

# 注册蓝图到app
app.register_blueprint(cms_bp)
app.register_blueprint(common_bp)
app.register_blueprint(front_bp)
app.register_blueprint(ued_bp)



if __name__ == '__main__':
    app.run()
