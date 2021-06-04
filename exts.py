# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_mail import Mail
from utils.alidayu import AlidayuAPI

# 用来发送邮件
mail = Mail()

# 用来获取短信验证 码
alidayu = AlidayuAPI()

# 用来进行docker 相关的操作
import docker
# mydocker = docker.DockerClient(base_url='unix://var/run/docker.sock')
mydocker = docker.DockerClient(base_url='tcp://192.168.141.177:2375')
if __name__ == '__main__':
    print(11111)
    pass
    # addflag = mydocker.containers.get('UWzFm9HtuC5zWkcXrjuR3P')
    # aa = addflag.exec_run("vim /flag.txt")
    # aa = addflag.exec_run("sh -c 'echo 123456 > /flag.txt'")
    # aa = addflag.exec_run("ls")
