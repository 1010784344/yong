# -*- coding: UTF-8 -*-


import os
import redis
import docker
from celery import Celery
from flask import Flask

import config
from exts import mail, main_docker


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


# 定义一个镜像上传任务
@celery.task
def image_up(img_url, name, file_name):
    task_path = os.path.join(config.UPLOADED_DIR, name)
    if not os.path.exists(task_path):
        os.makedirs(task_path)
    img_url.save(os.path.join(task_path, file_name))

    print("镜像上传成功！")


# 定义一个创建赛题的任务
@celery.task
def create_contest(tmp_uuid, work_id, task_name, task_image, port_name, task_flag, hos_tip):
    redis_ex = redis.Redis(host='127.0.0.1', port=6379, db=0)
    redis_ex.hset(work_id, 'progress', 0)

    # tar包 转移到对应的机器
    task_path = os.path.join(config.UPLOADED_DIR, task_name + os.sep + task_image)
    import shutil
    tmp_path = '/home/srv'
    # 本地 tar 包目录
    if hos_tip in ['192.168.141.177', '192.168.141.188']:
        real_path = tmp_path + os.sep + task_image
        if not os.path.exists(real_path):
            shutil.copy(task_path, tmp_path)
        # 如果是同一个主机就是同一个 docker
        my_docker = main_docker

    else:
        output = os.system('sshpass -p "123456" scp %s root@%s:/home/srv' % (task_path, hos_tip))
        # 如果是不同一个主机就新创建一个 docker
        my_docker = docker.DockerClient(base_url='tcp://%s:2375' % hos_tip)

    redis_ex.hset(work_id, 'progress', 20)
    try:
        # 检查 nginx 镜像是否存在（反向代理必须要有的镜像）
        img = my_docker.images.get("nginx")
        image_name = img.tags[0].split(':')[0]
    except Exception as e:
        print(task_path)
        # 加载镜像
        with open(task_path, 'rb') as fp:
            img = my_docker.images.load(fp.read())
            print(img[0].tags[0].split(':')[0])
            # 获取镜像名称
        image_name = img[0].tags[0].split(':')[0]
    redis_ex.hset(work_id, 'progress', 40)

    # image_name = 'nginx'
    # 创建代理容器

    redis_ex.hset(work_id, 'domain', '%s.testnginx.com' % tmp_uuid)

    # 赛题创建容器
    tmp_docker = my_docker.containers.run(
        image_name, name=tmp_uuid, ports={'80/tcp': (hos_tip, port_name)}, tty=True, detach=True)

    # import shortuuid
    # tmp_uuid = shortuuid.uuid()
    redis_ex.hset(work_id, 'progress', 60)

    # 配置代理配置文件
    conf_info = config.CONF_INFO % (tmp_uuid, hos_tip, port_name)
    f = open("/home/wang/nginx/conf.d/%s.conf" % tmp_uuid, "w")
    f.write(conf_info)
    f.close()

    redis_ex.hset(work_id, 'progress', 80)
    # 获取代理容器并再代理容器重新加载 nginx 配置文件
    pro = main_docker.containers.get("proxy-ng")
    pro.exec_run("nginx -s reload")

    if task_flag:
        add_flag = my_docker.containers.get(tmp_uuid)
        add_flag.exec_run("sh -c 'echo %s > /flag.txt'" % task_flag)

    redis_ex.hset(work_id, 'progress', 100)
    print(tmp_uuid)
    redis_ex.hset(work_id, 'workname', tmp_uuid)

    # redis_ex.hset(work_id, 'domain', '%s.testnginx.com' % tmp_uuid)
    print("赛题创建成功")


if __name__ == '__main__':
    pass





