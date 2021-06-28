# -*- coding: utf-8 -*-


import docker
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail


db = SQLAlchemy()

# 用来发送邮件
mail = Mail()

# 用来进行docker 相关的操作
# my_docker = docker.DockerClient(base_url='unix://var/run/docker.sock')
main_docker = docker.DockerClient(base_url='tcp://192.168.141.177:2375')


if __name__ == '__main__':
    pass

