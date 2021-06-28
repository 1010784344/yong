# -*- coding: UTF-8 -*-


from datetime import datetime
import shortuuid

from exts import db


# 添加 任务管理 的数据模型
class TaskModel(db.Model):

    __tablename__ = 'task'

    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, default=100)
    realscore = db.Column(db.Integer, default=0)
    type = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), nullable=True)
    text = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    flag = db.Column(db.String(255), nullable=False)
    creat_time = db.Column(db.DateTime, default=datetime.now)

    works = db.relationship('WorkModel', backref='tasks')


# 添加 work 的数据模型
class WorkModel(db.Model):

    __tablename__ = 'work'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_status = db.Column(db.String(255), nullable=True)
    task_time = db.Column(db.DateTime, default=datetime.now)
    task_score = db.Column(db.Integer, default=0)
    task_flag = db.Column(db.String(255), nullable=False)
    hostport = db.Column(db.String(255), nullable=True)
    task_name = db.Column(db.String(255), nullable=True)

    # 一个work只能属于一个赛题，一个work只能有一个人
    task_id = db.Column(db.String(100), db.ForeignKey('task.id'))
    author_id = db.Column(db.String(100), db.ForeignKey('front_user.id'), nullable=False)
    # host_id = db.Column(db.Integer,db.ForeignKey('host.id'))


class PortModel(db.Model):

    __tablename__ = 'port'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), default='5')
    host_id = db.Column(db.Integer, default=0)


class HostModel(db.Model):

    __tablename__ = 'host'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    ip = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    worknum = db.Column(db.Integer, default=0)
    syn_mirror = db.Column(db.String(255), nullable=True)
    # 一个主机有多个work
    # works = db.relationship('WorkModel', backref='hosts')
    # 一个host 可以使用多个端口
    # ports = db.relationship('PortModel', backref='rhost')


# 添加 轮播图弹窗 的数据模型
class BannersModel(db.Model):

    __tablename__ = 'banner'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    link_url = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.Integer, default=0)
    creat_time = db.Column(db.DateTime, default=datetime.now)


if __name__ == '__main__':
    pass
