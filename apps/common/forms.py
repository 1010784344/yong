# -*- coding: utf-8 -*-
from wtforms import Form,StringField
from wtforms.validators import regexp,input_required
import hashlib

# 定义获取手机号验证码表单
class SMSCaptchaForm(Form):
    salt = 'dktyudluyfjlhg;uifgdytfdj'
    telephone = StringField(validators=[regexp(r'1[345789]\d{9}')])
    timestamp = StringField(validators=[regexp(r'\d{13}')])
    sign = StringField(validators=[input_required()])


    # 重写 validate 函数
    def validate(self):
        result = super(SMSCaptchaForm,self).validate()

        # 如果父类的验证都不能通过，直接返回
        if not result:
            return False

        telephone = self.telephone.data
        timestamp = self.timestamp.data
        sign = self.sign.data

        # 后台生成加密参数并和前台进行比对
        sign2 = hashlib.md5((timestamp+telephone+self.salt).encode('utf-8')).hexdigest()
        if sign == sign2:
            return True
        else:
            return False






if __name__ == '__main__':
    print
    1