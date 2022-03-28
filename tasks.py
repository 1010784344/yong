# -*- coding: UTF-8 -*-


import os
import shutil
import docker
from celery import Celery
from flask import Flask

import config
from exts import redis_ex, celery_session
from apps.models import HostModel, WorkModel


# 初始化 一个新的app 对象
app = Flask(__name__)
app.config.from_object(config)


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
def create_contest(tmp_uuid, work_id, task_name, task_image, port_name, task_flag, hos_tip, image_flag):

    redis_ex.hset(work_id, 'progress', 0)

    # tar包 转移到对应的机器
    task_path = os.path.join(config.UPLOADED_DIR, task_name + os.sep + task_image)
    import shutil
    tmp_path = '/home/srv'
    # 本地 tar 包目录
    # if hos_tip in ['192.168.141.177', '192.168.141.188']:
    #     real_path = tmp_path + os.sep + task_image
    #     if not os.path.exists(real_path):
    #         shutil.copy(task_path, tmp_path)
    #     # 如果是同一个主机就是同一个 docker
    #     my_docker = main_docker
    #
    # else:
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
    f = open("/root/nginx/conf.d/%s.conf" % tmp_uuid, "w")
    # f = open("/home/wang/nginx/conf.d/%s.conf" % tmp_uuid, "w")
    f.write(conf_info)
    f.close()

    redis_ex.hset(work_id, 'progress', 80)
    # 获取代理容器并再代理容器重新加载 nginx 配置文件
    # pro = main_docker.containers.get("proxy-ng")
    pro.exec_run("nginx -s reload")

    if task_flag:
        add_flag = my_docker.containers.get(tmp_uuid)
        image_path = '/tmp/%s' % image_flag

        add_flag.exec_run("mkdir -p %s" % image_path)
        add_flag.exec_run("sh -c 'echo %s > %s/flag.txt'" % (task_flag, image_path))

    redis_ex.hset(work_id, 'progress', 100)
    print(tmp_uuid)
    redis_ex.hset(work_id, 'workname', tmp_uuid)

    # redis_ex.hset(work_id, 'domain', '%s.testnginx.com' % tmp_uuid)
    print("赛题创建成功")


# 定义一个删除赛题的任务
@celery.task
def del_contest(tmp_ip, tmp_name):
    # 获取赛题容器
    try:

        del_docker = docker.DockerClient(base_url='tcp://%s:2375' % tmp_ip)

        tmp_docker = del_docker.containers.get(tmp_name)
        tmp_docker.remove(force=True)

        conf_path = "/home/wang/nginx/conf.d/%s.conf" % tmp_name
        if os.path.exists(conf_path):
            os.remove(conf_path)
    except Exception as e:
        pass

    # pro = main_docker.containers.get("proxy-ng")
    pro.exec_run("nginx -s reload")
    print("任务删除成功！")
    # tmp_info = '任务 %s 删除成功！' % tmp_name
    # current_app.logger.info(tmp_info)


# 删除主机的所有资源
@celery.task
def del_all_source(tmp_ip):
    try:

        del_docker = docker.DockerClient(base_url='tcp://%s:2375' % tmp_ip)

        docker_list = del_docker.containers.list()
        for tmp_docker in docker_list:
            tmp_name = tmp_docker.name
            if tmp_name == 'proxy-ng':
                continue
            tmp_docker.remove(force=True)

            conf_path = "/root/nginx/conf.d/%s.conf" % tmp_name
            if os.path.exists(conf_path):
                os.remove(conf_path)

        res = celery_session.query(WorkModel).filter(WorkModel.host_port.like('%s%%' % tmp_ip)).delete(synchronize_session=False)

        celery_session.commit()
        celery_session.close()


    except Exception as e:
        pass


    print("资源删除成功！")


# 同步镜像到各个主机
@celery.task
def syn_all_source(task_name, task_image):

    try:
        task_path = os.path.join(config.UPLOADED_DIR, task_name + os.sep + task_image)
        tmp_path = '/home/srv'

        res = celery_session.query(HostModel).all()  # 返回表中所有数据对象

        for tmp_host in res:
            if str(tmp_host.is_main) == '1':
                real_path = tmp_path + os.sep + task_image
                if not os.path.exists(real_path):
                    shutil.copy(task_path, tmp_path)
            else:
                output = os.system('sshpass -p "123456" scp %s root@%s:/home/srv' % (task_path, tmp_host.ip))

    except Exception as e:
        pass

    print("资源同步成功！")


if __name__ == '__main__':
    pass





