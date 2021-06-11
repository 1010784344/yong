# -*- coding: UTF-8 -*-
import os
import redis
from celery import Celery
from flask import Flask
import config
from exts import mail,mydocker
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


# 定义一个镜像上传任务
@celery.task
def image_up(img_url,name,filename):
    taskpath = os.path.join(config.UPLOADED_dir, name)
    if not os.path.exists(taskpath):
        os.makedirs(taskpath)
    img_url.save(os.path.join(taskpath, filename))

    print("镜像上传成功！")


# 定义一个创建赛题的任务
@celery.task
def create_contest(tmpuuid,work_id,task_name,task_image,port_name,taskflag,hostip):


    redisex = redis.Redis(host='127.0.0.1', port=6379, db=0)
    redisex.hset(work_id, 'progress', 0)

    # tar包 转移到对应的机器（有可能跨机器暂未实现）
    taskpath = os.path.join(config.UPLOADED_dir, task_name + os.sep + task_image)
    import shutil
    tmppath = '/home/srv'
    # 本地 tar 包目录
    realpath = tmppath + os.sep + task_image
    if not os.path.exists(realpath):
        shutil.copy(taskpath, tmppath)

    redisex.hset(work_id, 'progress', 20)

    try:
        # 检查 nginx 镜像是否存在（反向代理必须要有的镜像）
        img = mydocker.images.get("nginx")
        imagename = img.tags[0].split(':')[0]
    except Exception as e:
        # 加载镜像
        with open(realpath, 'rb') as fp:
            img = mydocker.images.load(fp.read())
            # 获取镜像名称
        imagename = img[0].tags
    redisex.hset(work_id, 'progress', 40)

    # imagename = 'nginx'

    # 创建代理容器
    """



    """
    import shortuuid

    redisex.hset(work_id, 'domain', '%s.testnginx.com' % tmpuuid)

    # 赛题创建容器
    tmpdocker = mydocker.containers.run(imagename, name=tmpuuid, ports={'80/tcp': (hostip, port_name)},
                                        tty=True, detach=True)

    # import shortuuid
    # tmpuuid = shortuuid.uuid()
    redisex.hset(work_id, 'progress', 60)

    # 配置代理配置文件
    confinfo = config.CONF_info % (tmpuuid, port_name)
    f = open("/home/wang/nginx/conf.d/%s.conf" % tmpuuid, "w")
    f.write(confinfo)
    f.close()

    redisex.hset(work_id, 'progress', 80)
    # 获取代理容器并再代理容器重新加载 nginx 配置文件
    pro = mydocker.containers.get("proxy-ng")
    pro.exec_run("nginx -s reload")

    if taskflag:
        addflag = mydocker.containers.get(tmpuuid)
        addflag.exec_run("sh -c 'echo %s > /flag.txt'"%taskflag)

    redisex.hset(work_id, 'progress', 100)
    print(tmpuuid)
    redisex.hset(work_id, 'workname', tmpuuid)

    # redisex.hset(work_id, 'domain', '%s.testnginx.com' % tmpuuid)
    print("赛题创建成功")


if __name__ == '__main__':
    pass





