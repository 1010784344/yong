# -*- coding: utf-8 -*-
from apps.cms.views import cms_bp
import config
from flask import session,g
from apps.cms.models import CMSUser,CMPermission

# 优化后
# 提前利用钩子函数获取登录用户信息，并保存在全局变量 g
@cms_bp.before_request
def before_request():
    if config.CMS_USER_ID in session:
        user = CMSUser.query.filter_by(id=session[config.CMS_USER_ID]).first()
        if user:
            g.cms_user = user


# 给 cms 所有的模板都传入一个变量（权限）
@cms_bp.context_processor
def cms_context_processor():
    return {'CMPermission':CMPermission}



if __name__ == '__main__':
    print
    1