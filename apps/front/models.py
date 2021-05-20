# -*- coding: utf-8 -*-
from exts import db
import shortuuid
from datetime import datetime
import enum
from werkzeug.security import generate_password_hash,check_password_hash



class GenderEnum(enum.Enum):
    MALE = 1
    FEMALE = 2
    SECRET = 3
    UNKNOW = 4


class FrontUser(db.Model):
    __tablename__ = 'front_user'
    id = db.Column(db.String(100), primary_key= True,default=shortuuid.uuid)
    telephone = db.Column(db.String(11), nullable=True)
    username = db.Column(db.String(50),nullable=False)
    _password = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(50), unique= True)
    realname = db.Column(db.String(50))
    # 头像
    avatar = db.Column(db.String(100))
    signature = db.Column(db.String(100))
    gender = db.Column(db.Enum(GenderEnum),default=GenderEnum.UNKNOW)
    join_time = db.Column(db.DateTime,default=datetime.now)
    # 用户 与 帖子建立 一对多的关系
    posts = db.relationship('PostModel', backref='author')
    comments = db.relationship('CommentModel', backref='author')

    works = db.relationship('WorkModel', backref='author')











    def __init__(self,*args,**kwargs):
        if 'password' in kwargs:
            self.password = kwargs.get('password')
            # 把 password 取出来之后，从 kwargs 中去掉
            kwargs.pop('password')
        super(FrontUser,self).__init__(*args,**kwargs)


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









if __name__ == '__main__':
    print
    1