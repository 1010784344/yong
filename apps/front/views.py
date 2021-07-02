# -*- coding: utf-8 -*-

import os
import urllib.parse as urlparse

import shortuuid
import random
from flask import Blueprint, views, render_template, request, jsonify, session, url_for, g, abort, redirect, current_app
from flask_paginate import Pagination, get_page_parameter

from apps.front.forms import SignupForm, SignInForm
from apps.models import BannersModel, TaskModel, WorkModel, PortModel, HostModel
from apps.front.models import FrontUser
from apps.front.decorators import login_required
from exts import db, main_docker, redis_ex
import config
from tasks import create_contest


front_bp = Blueprint('front', __name__)


# 测试：注册完成跳转回上一个页面
@front_bp.route('/test/')
def test():
    return render_template('test.html')


# @front_bp.route('/')
# def index():
#     # 展示
#     banners = BannersModel.query.order_by(BannersModel.priority.desc()).limit(4)
#
#     # 排序信息(当没有st赋值，默认为 1 ，也就是当为首页时，st=1)
#     # st = request.args.get('st', type=int, default=1)
#
#     # 分页前
#     # posts = PostModel.query.all()
#
#     # 分页后
#     # 从 url 的查询参数获取当前是第几页(指定当前是第几页)
#     page = request.args.get(get_page_parameter(), type=int, default=1)
#
#     start = (page-1)*config.PER_PAGE
#     end = start + config.PER_PAGE
#
#     total = 0
#     query_obj = None
#
#     # 最新排序
#     # if st == 1:
#     query_obj = TaskModel.query.order_by(TaskModel.creat_time.desc())
#
#     posts = query_obj.slice(start, end)
#     total = query_obj.count()
#
#     # pagination 用于前台页面的上一页和下一页的控制
#     pagination = Pagination(bs_version=3, page=page, total=total)
#
#     # 返回多个参数到 html 页面
#     context = {'banners': banners,
#                'posts': posts,
#                'pagination': pagination,
#                # 方便前端点击那个板块，那个板块就选中的参数
#                }
#
#     return render_template('front/front_index.html', **context)

@front_bp.route('/', methods=['GET'])
@front_bp.route('/<int:page>', methods=['GET'])
def index(page=None):
    # 展示
    banners = BannersModel.query.order_by(BannersModel.priority.desc()).limit(4)

    if not page:
        page = 1

    tasks = TaskModel.query.order_by(TaskModel.creat_time.desc()).paginate(page=page, per_page=5)


    # 返回多个参数到 html 页面
    context = {'banners': banners,

               'tasks': tasks,
               }

    return render_template('front/front_index.html', **context)


# 任务详情
@front_bp.route('/t/<post_id>/')
def task_detail(post_id):
    post = TaskModel.query.get(post_id)

    ranks = WorkModel.query.filter_by(task_status=2, task_ori=post.name). \
        order_by(WorkModel.task_score.desc()).limit(5)

    if not post:
        # 如果帖子不存在，手动抛出一个异常
        abort(404)
    else:
        return render_template('front/front_tdetail.html', post=post, ranks=ranks)


# 创建任务
@front_bp.route('/acontest/<uuid>', methods=['GET'])
# @front_bp.route('/acontest/',methods=['GET'])
@login_required
def add_contest(uuid):
    # uuid = 'hakulamatata'
    task_id = request.args.get("task_id")

    task = TaskModel.query.get(task_id)

    if not task:
        return jsonify({'code': '400', 'message': '没有这个赛题！'})
    else:
        # 一个人一次只能做一道题，之前做到一半的题就会结束，做这道题，就会把上一道题干掉
        work = WorkModel(task_flag='', author_id=g.front_user.id)

        # 如果是动态 flag 添加 动态flag
        if task.type == 'dynamic':
            task_flag = shortuuid.uuid()
            work.task_flag = task_flag
        else:
            task_flag = ''

        work.task_name = shortuuid.uuid()
        work.writer = g.front_user
        work.task_ori = task.name

        # 获取空闲的主机
        host = db.session.query(HostModel).order_by(HostModel.worknum).first()
        host.worknum = host.worknum + 1
        tmp_ip = host.ip
        will_syn = host.syn_mirror
        will_syn_list = will_syn.split(',')
        if task.name not in will_syn_list:
            will_syn_list.append(task.name)
            host.syn_mirror = ','.join(will_syn_list)

        # 获取空闲的端口号
        port = PortModel.query.filter_by(status='5').first()
        tmp_port = port.name
        port.host_id = host.id

        work.host_port = '%s:%s' % (tmp_ip, tmp_port)
        work.task_status = '1'

        # 容器创建完毕之后，修改port 的状态
        port.status = "10"

        # 将创建信息添加到日志里面
        tmp_info = "%s 基于 %s 赛题创建了一个任务 %s" % (g.front_user.username, task.name, work.task_name)
        current_app.logger.info(tmp_info)

        # 异步启动创建流程
        create_contest.delay(work.task_name, uuid, task.name, task.image, port.name, task_flag, host.ip)
        """
        uuid 前端传递过来的进度唯一标识
        taskflag 动态flag
        work.task_name  任务的名称（容器的名称）
        
        """

        db.session.add(work)
        db.session.commit()

        return jsonify({'code': '200', 'message': '成功！'})


# 重新创建
@front_bp.route('/rcontest/<uuid>', methods=['GET'])
@login_required
def rcontest(uuid):
    # 先删除当前的 work
    work_name = request.args.get('work_name')
    work = WorkModel.query.filter_by(task_name=work_name).first()
    taskid = work.task_id

    work.task_status = 2
    tmpname = work.task_name
    tmpport = work.host_port.split(':')[1]

    tmpip = work.host_port.split(':')[0]

    port = PortModel.query.filter_by(name=tmpport).first()
    port.status = '5'
    port.host_id = 0

    host = HostModel.query.filter_by(ip=tmpip).first()
    host.worknum = host.worknum - 1

    # redis_ex = redis.Redis(host='127.0.0.1', port=6379, db=0)
    # redis_ex.hdel(work.id, 'progress')
    # redis_ex.hdel(work.id, 'domain')
    import docker
    del_docker = docker.DockerClient(base_url='tcp://%s:2375' % tmpip)
    # 获取赛题容器
    tmp_docker = del_docker.containers.get(tmpname)
    tmp_docker.remove(force=True)

    conf_path = "/home/wang/nginx/conf.d/%s.conf" % tmpname
    if os.path.exists(conf_path):
        os.remove(conf_path)

    pro = main_docker.containers.get("proxy-ng")
    pro.exec_run("nginx -s reload")

    db.session.delete(work)
    db.session.commit()

    return redirect(url_for('front.add_contest', uuid=uuid, task_id=taskid))


# 提交答案
@front_bp.route('/aanswer/', methods=['GET'])
@login_required
def aanswer():
    if request.method == 'GET':
        work_name = request.args.get('work_name')
        flag_info = request.args.get('flaginfo')

        work = WorkModel.query.filter_by(task_name=work_name).first()
        real_flag = work.task_flag
        if not real_flag:
            quiet_id = work.task_id
            task = TaskModel.query.filter_by(id=quiet_id).first()
            real_flag = task.flag
        if flag_info != real_flag:

            work.task_score = random.randint(60,95)
            work.task_status = 2
            db.session.commit()
            return jsonify({'code': '200', 'message': '回答错误！'})
        else:
            work.task_score = 100
            work.task_status = 2

            db.session.commit()

            return jsonify({'code': '200', 'message': '回答正确！'})


@front_bp.route('/show_progress/<uuid>')
def show_progress(uuid):
    """前端请求进度的函数"""

    try:
        tmp_data = redis_ex.hget(uuid, 'progress')
        if not tmp_data:
            tmp_data = 0
        domain = redis_ex.hget(uuid, 'domain')
        work_name = redis_ex.hget(uuid, 'workname')
    except Exception as e:
        tmp_data = 0
        domain = 'hello'

    return jsonify({'res': tmp_data, 'domains': domain, 'workname': work_name})


@front_bp.route('/flogout/')
@login_required
def flog_out():
    session.pop(config.FRONT_USER_ID)
    return redirect(url_for('front.sign_in'))


class SignupView(views.MethodView):

    def get(self):
        # 获取上一个页面的 url
        return_to = request.referrer
        if return_to:
            return_to = urlparse.urlparse(return_to).path

        # 不能跳转到本页面和注册页面
        if return_to and return_to != request.url and return_to != url_for('front.signup'):
            return render_template('front/front_signup.html', return_to=return_to)
        else:
            return render_template('front/front_signup.html')

    def post(self):
        form = SignupForm(request.form)

        if form.validate():
            # telephone = form.telephone.data
            username = form.username.data
            password = form.password.data
            user = FrontUser(username=username, password=password)
            db.session.add(user)
            db.session.commit()

            return jsonify({'code': '200', 'message': '用户注册成功！'})
        else:
            message = form.errors.popitem()[1][0]

            # 表单验证错误（数据格式不对）
            return jsonify({'code': '400', 'message': message})


class SignInView(views.MethodView):

    def get(self):
        # 获取上一个页面的 url
        return_to = request.referrer
        if return_to:
            return_to = urlparse.urlparse(return_to).path

        # 不能跳转到本页面及注册页面
        if return_to and return_to != request.url and return_to != url_for('front.signup'):
            return render_template('front/front_signin.html', return_to=return_to)
        else:
            return render_template('front/front_signin.html')

    def post(self):
        form = SignInForm(request.form)
        password = form.password.data

        print(password)
        if form.validate():
            username = form.telephone.data
            password = form.password.data
            remeber = form.remember.data

            print(password)

            user = FrontUser.query.filter_by(username=username).first()

            if user and user.check_password(password):
                session[config.FRONT_USER_ID] = user.id
                if remeber:
                    session.permanent = True
                return jsonify({'code': '200', 'message': '用户登录成功！'})
            else:

                return jsonify({'code': '400', 'message': '用户手机或者密码错误！'})
        else:
            message = form.errors.popitem()[1][0]
            # 表单验证错误（数据格式不对）
            return jsonify({'code': '400', 'message': message})


front_bp.add_url_rule('/signup/', view_func=SignupView.as_view('signup'))
front_bp.add_url_rule('/signin/', view_func=SignInView.as_view('sign_in'))
