# -*- coding: utf-8 -*-
from wtforms import Form,StringField,IntegerField
from wtforms.validators import Email,input_required,length,EqualTo,ValidationError
from utils import zlmemcache
from flask import g


class LoginForm(Form):
    email = StringField(validators=[input_required(message='请输入邮箱')])
    password = StringField(validators=[length(6,15,message='请输入正确格式的密码'),input_required(message='请输入密码')])
    # 刚开始这个值空的，如果用户点击 remember me 之后，form.remember.data 就会有值
    remember = IntegerField()


class ResetpwdForm(Form):
    oldpwd = StringField(validators=[length(6,15,message='请输入正确格式的旧密码'),input_required(message='请输入旧密码')])
    newpwd = StringField(validators=[length(6,20,message="请输入正确格式的新密码")])
    newpwd2 = StringField(validators=[EqualTo('newpwd',message='请确认新密码和旧密码保持一致！'),input_required(message='请输入新密码')])


class ResetemailForm(Form):
    email = StringField(validators=[])
    captcha = StringField(validators=[length(6,6,message="请输入正确格式的验证码")])

    # 下面这2个函数是 WTForms 自定义的表单验证器
    # 验证码不一致的问题
    def validate_captcha(self,field):
        email =self.email.data
        captcha = field.data
        captcha_cache = zlmemcache.get(email)


        if not captcha_cache or captcha_cache.lower() != captcha.lower():
            raise ValidationError('邮箱验证码错误')

    #输入的邮箱相同的问题
    def validate_email(self,field):
        email = field.data
        user = g.cms_user

        if email == user.email:
            raise ValidationError('不能修改为相同邮箱！')

# 添加 轮播图弹窗 的表单验证
class AddBannerForm(Form):
    name = StringField(validators=[input_required(message='请输入轮播图名称!')])
    img_url = StringField(validators=[input_required(message='请输入轮播图图片链接！')])
    link_url = StringField(validators=[input_required(message='请输入轮播图跳转链接！')])
    priority = StringField(validators=[input_required(message='请输入轮播图优先级！')])

# 添加 任务弹窗 的表单验证
class AddTaskForm(Form):
    name = StringField(validators=[input_required(message='请输入任务名称!')])
    img_url = StringField(validators=[])
    link_url = StringField(validators=[input_required(message='请输入轮播图跳转链接！')])
    priority = StringField(validators=[input_required(message='请输入轮播图优先级！')])


# 编辑 轮播图弹窗 的表单验证
class UpdateBannerForm(Form):
    name = StringField(validators=[input_required(message='请输入轮播图名称!')])
    img_url = StringField(validators=[input_required(message='请输入轮播图图片链接！')])
    link_url = StringField(validators=[input_required(message='请输入轮播图跳转链接！')])
    priority = StringField(validators=[input_required(message='请输入轮播图优先级！')])
    banner_id = IntegerField(validators=[input_required(message='请输入轮播图id！')])

# 添加 板块 的表单验证
class AddBoardForm(Form):
    name = StringField(validators=[input_required(message='请输入板块名称!')])

# 编辑 板块 的表单验证
class UpdateBoardForm(Form):
    name = StringField(validators=[input_required(message='请输入板块名称!')])
    board_id = IntegerField(validators=[input_required(message='请输入板块id！')])


if __name__ == '__main__':
    print
    1