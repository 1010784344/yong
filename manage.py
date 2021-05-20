# -*- coding: utf-8 -*-
from myContest import app
from exts import db
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

from apps.cms import models as cms_modles
from apps.front import models as front_modles
from apps import models as apps_modles

CMSUser = cms_modles.CMSUser
CMSRole = cms_modles.CMSRole
CMPermission = cms_modles.CMPermission

PostModel = apps_modles.PostModel
BoardModel = apps_modles.BoardModel

FrontUser = front_modles.FrontUser
# flask_script 里的 manager（有了这个才会支持在命令行执行代码的行为）
# flask_script 的 manager 对象是执行所有命令的发号施令者（）
manager = Manager(app)

#创建子命令(flask_migrate 说白了就是我们这里另一个文件里配置的子命令，
# flask_migrate 这个模块功能相对来说就是比较简单，就是只是数据库迁移，
# 且封装在一个子命令里面)
Migrate(app,db)

# 将子命令添加到发号施令者（命令行）上面
manager.add_command('db',MigrateCommand)

# python .\manage.py create_cms_user -u 1010784344 -p 123456 -e 1010784344@qq.com
# 给 manager.py 添加一条命令:在 manage.py 通过 flask-script 给 cms 添加一个用户
@manager.option('-u','--username',dest='username')
@manager.option('-p','--password',dest='password')
@manager.option('-e','--email',dest='email')
def create_cms_user(username,password,email):
    user = CMSUser(username=username,password=password,email=email)
    db.session.add(user)
    db.session.commit()
    print('cms 用户添加成功！')



# python .\manage.py add_cms_role
# 运用 flask_script 添加命令的实战（不需要传递参数）
# 给系统添加所有的角色
@manager.command
def add_cms_role():
    # 1.访问者（可以修改个人信息）
    vistors = CMSRole(name='访问者',desc='只能相关数据，不能修改。')
    vistors.permissions = CMPermission.VISITOR

    # 2.运营角色（修改个人信息，管理帖子，管理评论，管理前台用户。）
    operator = CMSRole(name='运营',desc='管理帖子，管理评论，管理前台用户。')
    operator.permissions = CMPermission.VISITOR|CMPermission.POSTER|CMPermission.CMSUSER\
    |CMPermission.COMMENTER|CMPermission.FRONTUSER

    # 3.管理员（拥有绝大部分权限）
    admin = CMSRole(name='管理员', desc='拥有本系统所有权限。')
    admin.permissions = CMPermission.VISITOR | CMPermission.POSTER | CMPermission.CMSUSER \
                           | CMPermission.COMMENTER | CMPermission.FRONTUSER | CMPermission.BOARDER

    # 4.开发者
    developer = CMSRole(name='开发者', desc='开发人员专用角色。')
    developer.permissions = CMPermission.ALL_PERMISSION

    db.session.add_all([vistors,operator,admin,developer])
    db.session.commit()


# 注意：这里验证的是数据库里面的第一个用户
# 这个其实没有啥，只不过让把 models.py 里的 has_permission 函数封装在命令行里面去了
# 判断某个用户有没有访问者的权限
@manager.command
def test_permission():
    # 用法：python manage.py test_permission

    user = CMSUser.query.first()
    result = user.has_permission(CMPermission.VISITOR)
    if result:
        print('这个用户有访问者的权限！')
    else:
        print('这个用户没有访问者的权限！')



# 用法：python manage.py add_user_role -e 1010784344@qq.com -n 访问者
# 给某个用户添加一个角色
@manager.option('-e','--email',dest='email')
@manager.option('-n','--name',dest='name')
def add_user_role(email,name):
    user = CMSUser.query.filter_by(email=email).first()
    if user:
        role = CMSRole.query.filter_by(name=name).first()
        if role:
            user.roles.append(role)
            db.session.commit()
            print('用户添加到角色成功！')
        else:
            print('%s没有这个角色%s！' %role)

    else:
        print('%s邮箱没有这个用户！'%email)





# 添加一个前台用户
@manager.option('-t','--telephone',dest='telephone')
@manager.option('-p','--password',dest='password')
@manager.option('-u','--username',dest='username')
def create_front_user(telephone,password,username):
    user = FrontUser(telephone=telephone,password=password,username=username)

    db.session.add(user)
    db.session.commit()

    print('前台用户添加成功！')


# 命令行批量创建测试帖子
@manager.command
def create_test_post():

    board = BoardModel.query.first()
    author = FrontUser.query.first()

    for i in range(0,100):
        title = '标题：%s'%i
        content = '内容：%s'%i

        post = PostModel(title=title, content=content)

        post.boards = board
        post.author = author

        db.session.add(post)
        db.session.commit()
    print('恭喜！测试帖子添加成功！')







if __name__ == '__main__':
    manager.run()