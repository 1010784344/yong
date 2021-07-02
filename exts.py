# -*- coding: utf-8 -*-

import redis
import docker
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

# 用来进行docker 相关的操作
# my_docker = docker.DockerClient(base_url='unix://var/run/docker.sock')
main_docker = docker.DockerClient(base_url='tcp://172.16.1.171:2375')
redis_ex = redis.Redis(host='127.0.0.1', port=6379, db=0)

if __name__ == '__main__':
    pass

