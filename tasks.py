# -*- coding: UTF-8 -*-

from celery import Celery
from flask import Flask
import config
from exts import mail
from flask_mail import Message

# 初始化 一个新的app 对象
app = Flask(__name__)
app.config.from_object(config)

mail.init_app(app)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# 初始化 celery 对象
celery = make_celery(app)



# 定义一个发送验证码任务
@celery.task
def send_email(subject,recipients,body):

    message = Message(subject=subject,recipients=recipients,body=body)

    mail.send(message)


if __name__ == '__main__':
    pass





if __name__ == '__main__':
    pass