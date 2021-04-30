# -*- coding: UTF-8 -*-

from apps.front.views import front_bp
import config
from flask import session,g,render_template
from apps.front.models import FrontUser

# 优化后
# 提前利用钩子函数获取登录用户信息，并保存在全局变量 g
@front_bp.before_request
def my_before_request():
    if config.FRONT_USER_ID in session:
        user = FrontUser.query.filter_by(id=session[config.FRONT_USER_ID]).first()
        if user:
            g.front_user = user


# 根据错误状态码（404或者500）定制对应的页面显示
@front_bp.errorhandler(404)
def page_not_found(error):
    return render_template('front/front_404.html'),404

if __name__ == '__main__':
    pass