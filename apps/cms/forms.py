# -*- coding: utf-8 -*-


from wtforms import Form, StringField, IntegerField
from wtforms.validators import input_required, length


class LoginForm(Form):
    email = StringField(validators=[input_required(message='请输入邮箱')])
    password = StringField(validators=[length(6, 15, message='请输入正确格式的密码'), input_required(message='请输入密码')])
    # 刚开始这个值空的，如果用户点击 remember me 之后，form.remember.data 就会有值
    remember = IntegerField()


# 添加 镜像弹窗 的表单验证
class AddTaskForm(Form):
    name = StringField(validators=[input_required(message='请输入任务名称!')])
    img_url = StringField(validators=[])
    link_url = StringField(validators=[input_required(message='请输入轮播图跳转链接！')])
    priority = StringField(validators=[input_required(message='请输入轮播图优先级！')])
    type_radio = StringField(validators=[])


# 添加 主机弹窗 的表单验证
class AddHostForm(Form):
    name = StringField(validators=[input_required(message='请输入主机名称!')])
    ip = StringField(validators=[])


if __name__ == '__main__':
    pass
