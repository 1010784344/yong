# -*- coding: utf-8 -*-


from flask import Flask
from flask_wtf import CSRFProtect
import logging

from exts import db
from apps.cms.views import cms_bp
from apps.front.views import front_bp
import config


app = Flask(__name__)

# 日志系统配置
app.logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('/var/log/myContest.log', encoding='UTF-8')
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

# 引入配置文件
app.config.from_object(config)

# 注册 sqlalchemy 到 app 里面
db.init_app(app)

# csrf 保护
CSRFProtect(app)

# 注册蓝图到app
app.register_blueprint(cms_bp)
app.register_blueprint(front_bp)


@app.template_filter('host_status')
def host_status(value):
    value = '离线' if value == '0' else '在线'
    return value


if __name__ == '__main__':
    app.run(host='0.0.0.0')
