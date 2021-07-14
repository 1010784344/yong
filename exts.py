# -*- coding: utf-8 -*-

import redis
import docker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


db = SQLAlchemy()

# 用来进行docker 相关的操作
# my_docker = docker.DockerClient(base_url='unix://var/run/docker.sock')
main_docker = docker.DockerClient(base_url='tcp://172.16.1.171:2375')
redis_ex = redis.Redis(host='127.0.0.1', port=6379, db=0)


# 创建数据库引擎
engine = create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/zlbbs")
# 引擎来创建一个session，后面才能通过session与数据库进行交互。
Session = sessionmaker(engine)
celery_session = Session()



if __name__ == '__main__':
    pass

