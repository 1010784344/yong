# -*- coding: utf-8 -*-


from wtforms import Form, StringField
from wtforms.validators import Regexp, EqualTo


class SignupForm(Form):
    username = StringField(validators=[Regexp(r'.{3,15}', message='用户名长度在3-15位之间')])
    password = StringField(validators=[Regexp(r'[0-9a-zA-Z_\.]{6,15}', message='请输入正确格式的密码')])
    password2 = StringField(validators=[EqualTo('password', message='两次输入的密码不一致')])


class SignInForm(Form):
    telephone = StringField()
    password = StringField(validators=[Regexp(r'[0-9a-zA-Z_\.]{6,15}', message='请输入正确格式的密码')])
    remember = StringField()


if __name__ == '__main__':
    pass
