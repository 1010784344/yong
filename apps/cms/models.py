# -*- coding: utf-8 -*-
from exts import db
from datetime import datetime
from werkzeug.security import check_password_hash,generate_password_hash

# 从这来看，这个类就只是相当于一个全局变量，也没有具体的方法
class CMPermission(object):
    # 代表所有的权限
    ALL_PERMISSION = 0b11111111
    # 1.访问者的权限
    VISITOR = 0b00000001
    # 2.管理帖子的权限
    POSTER = 0b00000010
    # 3.管理评论的权限
    COMMENTER = 0b00000100
    # 4.管理板块的权限
    BOARDER = 0b00001000
    # 5.管理前台用户的权限
    FRONTUSER = 0b00010000
    # 6.管理后台用户的权限
    CMSUSER = 0b00100000
    # 7.管理后台管理员的权限
    ADMINER = 0b01000000


cms_user_role = db.Table('cms_user_role',
    db.Column('CMSRole_id',db.Integer,db.ForeignKey('cms_role.id'), primary_key=True),
    db.Column('CMSUser_id',db.Integer,db.ForeignKey('cms_user.id'), primary_key=True))


class CMSRole(db.Model):

    __tablename__ = 'cms_role'

    id = db.Column(db.Integer, primary_key= True,autoincrement= True)
    name = db.Column(db.String(50),nullable=False)
    desc = db.Column(db.String(200),nullable=True)
    create_time = db.Column(db.DateTime,default=datetime.now)
    permissions = db.Column(db.Integer,default=CMPermission.VISITOR)
    users = db.relationship('CMSUser',secondary=cms_user_role, backref='roles')




class CMSUser(db.Model):
    __tablename__ = 'cms_user'
    id = db.Column(db.Integer, primary_key= True,autoincrement= True)
    username = db.Column(db.String(50),nullable=False)
    _password = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(50),nullable=False, unique= True)
    join_time = db.Column(db.DateTime,default=datetime.now)

    def __init__(self,username,password,email):
        self.username = username
        # 这里的 self.password 其实执行的 @property.setter 里的方法,其实是给 _password 赋了值
        self.password = password
        self.email = email

    # password属性（方法）获取值
    @property
    def password(self):
        return self._password

    # password属性（方法）赋值
    @password.setter
    def password(self, rawpassword):
        self._password = generate_password_hash(rawpassword)

    def check_password(self,rawpassword ):
        result = check_password_hash(self.password,rawpassword)
        return result

    # 根据角色获取用户的权限
    @property
    def permissions(self):
        all_permissions = 0
        if not self.roles:
            pass
        else:
            for role in self.roles:
                all_permissions |= role.permissions
        return all_permissions

    # 比较用户的权限和输入的权限是否一致
    def has_permission(self,permission):
        all_permissions = self.permissions
        result = all_permissions & permission
        return result

    # 判断用户是否为开发人员
    @property
    def is_developer(self):
        return self.has_permission(CMPermission.ALL_PERMISSION)




if __name__ == '__main__':
    print
    1