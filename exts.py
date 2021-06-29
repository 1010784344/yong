# -*- coding: utf-8 -*-


import docker
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# 用来进行docker 相关的操作
# my_docker = docker.DockerClient(base_url='unix://var/run/docker.sock')
main_docker = docker.DockerClient(base_url='tcp://172.16.1.171:2375')


if __name__ == '__main__':
    pass

