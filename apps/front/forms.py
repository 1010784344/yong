# -*- coding: utf-8 -*-
from wtforms import Form,StringField
from wtforms.validators import Regexp,EqualTo,ValidationError,InputRequired
from utils import zlmemcache



class SignupForm(Form):
    # telephone=StringField(validators=[Regexp(r'1[3578]\d{9}',message='请输入正确格式的手机号码')])
    # sms_captcha=StringField(validators=[Regexp(r'\w{4}',message='请输入四位短信验证码')])
    username=StringField(validators=[Regexp(r'.{3,15}',message='用户名长度在3-15位之间')])
    password=StringField(validators=[Regexp(r'[0-9a-zA-Z_\.]{6,15}',message='请输入正确格式的密码')])
    password2=StringField(validators=[EqualTo('password',message='两次输入的密码不一致')])
    # graph_captcha=StringField(validators=[Regexp(r'\w{4}',message='图形验证码不正确')])


    # 验证某一个字段是否正确
    def validate_sms_captcha(self,field):
        sms_captcha = field.data
        telephone = self.telephone.data

        if sms_captcha != '1111':#测试用
            mem_sms_captcha = zlmemcache.get(telephone)
            if not mem_sms_captcha or mem_sms_captcha.lower() != sms_captcha.lower():
                raise ValidationError(message='短信验证码错误！')

    # 验证某一个字段是否正确
    def validate_graph_captcha(self,field):
        graph_captcha = field.data

        if graph_captcha != '1111':#测试用
            mem_graph_captcha = zlmemcache.get(graph_captcha.lower())
            if not mem_graph_captcha:
                raise ValidationError(message='图形验证码错误！')



class SigninForm(Form):
    telephone = StringField()
    password = StringField(validators=[Regexp(r'[0-9a-zA-Z_\.]{6,15}',message='请输入正确格式的密码')])
    remember = StringField()



class AddPostForm(Form):
    title = StringField(validators=[InputRequired(message='请输入标题！')])
    content = StringField(validators=[InputRequired(message='请输入内容！')])
    board_id = StringField(validators=[InputRequired(message='请输入板块 id！')])



class AddCommentForm(Form):
    content = StringField(validators=[InputRequired(message='请输入内容！')])
    post_id = StringField(validators=[InputRequired(message='请输入帖子 id！')])


if __name__ == '__main__':
    print
    1