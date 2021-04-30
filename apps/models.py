# -*- coding: UTF-8 -*-
from exts import db
from datetime import datetime

# 添加 轮播图弹窗 的数据模型

class BannersModel(db.Model):

    __tablename__ = 'banner'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(255),nullable=False)
    image_url = db.Column(db.String(255),nullable=False)
    link_url = db.Column(db.String(255),nullable=False)
    priority = db.Column(db.Integer,default=0)
    creat_time = db.Column(db.DateTime,default=datetime.now)


# 添加 板块管理 的数据模型
class BoardModel(db.Model):

    __tablename__ = 'board'

    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(255),nullable=False)
    creat_time = db.Column(db.DateTime,default=datetime.now)

    posts = db.relationship('PostModel', backref='boards')


# 添加 帖子 的数据模型
class PostModel(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key= True,autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text,nullable=False)
    create_time = db.Column(db.DateTime,default=datetime.now)

    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))
    # 用户 与 帖子建立 一对多的关系
    author_id = db.Column(db.String(100),db.ForeignKey('front_user.id'),nullable=False)
    comments = db.relationship('CommentModel', backref='posts')

    # 加精与帖子建立的好像是一对一的关系
    highlight = db.relationship('HighlightPostModel', backref='posts')

# 添加 评论 的数据模型
class CommentModel(db.Model):

    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key= True,autoincrement=True)
    content = db.Column(db.Text,nullable=False)
    create_time = db.Column(db.DateTime,default=datetime.now)

    #一个评论只能属于一个帖子，一个评论只能有一个作者
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    author_id = db.Column(db.String(100),db.ForeignKey('front_user.id'),nullable=False)



# 加精的帖子数据模型
class HighlightPostModel(db.Model):
    __tablename__ = 'highlight_post'
    id = db.Column(db.Integer, primary_key= True,autoincrement=True)
    create_time = db.Column(db.DateTime,default=datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

if __name__ == '__main__':
    pass