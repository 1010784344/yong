# -*- coding: utf-8 -*-


import os

from flask import Blueprint, render_template, views, request, redirect, url_for, session, jsonify, current_app

from apps.cms.forms import LoginForm, AddTaskForm, AddHostForm
from apps.cms.models import CMSUser
from apps.models import TaskModel, WorkModel, HostModel, PortModel
import config
from apps.cms.decorators import login_required
from exts import db, main_docker
from utils import checkip
from tasks import del_contest, del_all_source, syn_all_source


# 定义 cms 的蓝图
cms_bp = Blueprint('cms', __name__, url_prefix='/cms')


# cms 首页
@cms_bp.route('/index/')
@login_required
def index():
    return render_template('/cms/cms_index.html')


# cms 注销
@cms_bp.route('/logout/')
@login_required
def logout():
    session.pop(config.CMS_USER_ID)
    return redirect(url_for('cms.login'))


# cms 个人中心
@cms_bp.route('/profile/')
@login_required
def profile():

    return render_template('cms/cms_profile.html')


# 主机管理
@cms_bp.route('/hosts')
@cms_bp.route('/hosts/<int:page>')
@login_required
def hosts(page=None):

    if not page:
        page = 1

    all_host = HostModel.query.order_by(HostModel.create_time.desc()).paginate(page=page, per_page=5)
    # for tmp_host in all_host:
    #     tmp_ip = tmp_host.ip
    #     if not checkip.ping_all(tmp_ip):
    #         tmp_host.status = 0
    #     else:
    #         tmp_host.status = 1
    # db.session.commit()

    # all_host = HostModel.query.all()

    return render_template('cms/cms_hosts.html', all_host=all_host)


# 主机是否在线状态轮询
@cms_bp.route("/ip_status", methods=["GET"])
def ip_status():
    host_info = {}
    all_host = HostModel.query.all()
    for tmp_host in all_host:
        tmp_ip = tmp_host.ip
        if not checkip.ping_all(tmp_ip):
            tmp_host.status = '0'
        else:
            tmp_host.status = '1'
        host_info[tmp_host.id] = '在线' if tmp_host.status == '1' else '离线'
    db.session.commit()

    return jsonify(host_info)


# 添加主机弹窗 的提交表单
@cms_bp.route('/add_host/', methods=['POST'])
@login_required
def add_host():

    form = AddHostForm(request.form)

    if form.validate():
        name = form.name.data
        ip = form.ip.data
        is_main = form.is_main.data
        check_res = checkip.test_ip(ip)
        if not check_res:
            return jsonify({'code': '400', 'message': 'ip 输入有误，请重新输入！'})

        # 真实添加主机
        # checkip.add_ip(ip)
        if is_main == '1':
            host = HostModel(name=name, ip=ip, status='1', is_main='1', syn_mirror=',')
        else:
            host = HostModel(name=name, ip=ip, status='1', syn_mirror=',')

        db.session.add(host)
        db.session.commit()

        return jsonify({'code': '200', 'message': '主机添加成功！'})
    else:

        message = form.errors.popitem()[1][0]
        # 表单验证错误（数据格式不对）

        return jsonify({'code': '400', 'message': message})


# 删除主机弹窗 的提交表单
@cms_bp.route('/del_host/', methods=['POST'])
@login_required
def del_host():

    host_id = request.form.get('banner_id')

    if not host_id:
        return jsonify({'code': '400', 'message': '主机id不存在！'})

    host = HostModel.query.get(host_id)
    if not host:
        return jsonify({'code': '400', 'message': '主机不存在！'})

    del_all_source.delay(host.ip)
    # del_all_source(host.ip)

    db.session.delete(host)
    db.session.commit()
    return jsonify({'code': '200', 'message': '主机删除成功！'})


# 任务管理
@cms_bp.route('/works')
@cms_bp.route('/works/<int:page>')
@login_required
def works(page=None):

    if not page:
        page = 1

    all_work = WorkModel.query.order_by(WorkModel.task_time.desc()).paginate(page=page, per_page=5)

    return render_template('cms/cms_works.html', all_work=all_work)


# 镜像管理
@cms_bp.route('/tasks')
@cms_bp.route('/tasks/<int:page>')
@login_required
def tasks(page=None):

    if not page:
        page = 1

    all_task = TaskModel.query.order_by(TaskModel.creat_time.desc()).paginate(page=page, per_page=5)

    return render_template('cms/cms_tasks.html', all_task=all_task)


# 添加镜像弹窗 的提交表单
@cms_bp.route('/add_task/', methods=['POST'])
@login_required
def add_task():

    form = AddTaskForm(request.form)

    if form.validate():
        name = form.name.data
        img_url = request.files['img_url']
        flag_url = form.link_url.data
        text = form.priority.data
        tmp_type = form.type_radio.data
        filename = img_url.filename
        if tmp_type == '1':
            opt_type = 'static'
        elif tmp_type == '2':
            opt_type = 'dynamic'
        # image_up.delay(img_url,name,filename)
        task_path = os.path.join(config.UPLOADED_DIR, name)
        if not os.path.exists(task_path):
            os.makedirs(task_path)
        img_url.save(os.path.join(task_path, filename))

        task = TaskModel(name=name, image=filename, flag=flag_url, text=text, type=opt_type)

        db.session.add(task)
        db.session.commit()

        # 同步镜像资源到其他的主机
        syn_all_source.delay()
        # syn_all_source(name, filename)

        return jsonify({'code': '200', 'message': '镜像添加成功！'})
    else:

        message = form.errors.popitem()[1][0]

        # 表单验证错误（数据格式不对）
        return jsonify({'code': '400', 'message': message})


# 删除镜像弹窗 的提交表单
@cms_bp.route('/del_task/', methods=['POST'])
@login_required
def del_task():

    task_id = request.form.get('banner_id')

    if not task_id:
        return jsonify({'code': '400', 'message': '镜像id不存在！'})

    task = TaskModel.query.get(task_id)
    if not task:
        return jsonify({'code': '400', 'message': '镜像不存在！'})

    name = task.name
    image_name = task.image

    task_path = os.path.join(config.UPLOADED_DIR, name)
    image_path = os.path.join(task_path, image_name)
    if os.path.exists(image_path):
        os.remove(image_path)

    db.session.delete(task)
    db.session.commit()
    return jsonify({'code': '200', 'message': '镜像删除成功！'})


# 删除任务弹窗 的提交表单
@cms_bp.route('/del_work/', methods=['GET'])
@login_required
def del_work():

    work_id = request.args.get('banner_id')

    if not work_id:
        return jsonify({'code': '400', 'message': '任务id不存在！'})

    work = WorkModel.query.get(work_id)
    work.task_status = 2
    if not work:
        return jsonify({'code': '400', 'message': '任务不存在！'})

    tmp_name = work.task_name
    tmp_port = work.host_port.split(':')[1]

    tmp_ip = work.host_port.split(':')[0]

    port = PortModel.query.filter_by(name=tmp_port).first()
    port.status = '5'
    port.host_id = 0

    host = HostModel.query.filter_by(ip=tmp_ip).first()

    if not host:
        db.session.delete(work)
        db.session.commit()

        return jsonify({'code': '200', 'message': '任务删除成功！'})

    if host.work_num <= 0:
        host.work_num = 0
    else:
        host.work_num = host.work_num - 1

    del_contest.delay(tmp_ip, tmp_name)

    # # 获取赛题容器
    # try:
    #     import docker
    #     del_docker = docker.DockerClient(base_url='tcp://%s:2375' % tmp_ip)
    #
    #     tmp_docker = del_docker.containers.get(tmp_name)
    #     tmp_d                                               ocker.remove(force=True)
    #
    #     conf_path = "/home/wang/nginx/conf.d/%s.conf" % tmp_name
    #     if os.path.exists(conf_path):
    #         os.remove(conf_path)
    # except Exception as e:
    #     pass
    #
    # pro = main_docker.containers.get("proxy-ng")
    # pro.exec_run("nginx -s reload")
    #
    # tmp_info = '任务 %s 删除成功！' % tmp_name
    # current_app.logger.info(tmp_info)

    db.session.delete(work)
    db.session.commit()

    return jsonify({'code': '200', 'message': '任务删除成功！'})


# 前台用户管理
@cms_bp.route('/fusers/')
@login_required
# @permission_required(CMPermission.FRONTUSER)
def front_users():
    return render_template('cms/cms_fusers.html')


# cms 登录
# 基于调度方法的类视图
class LoginView(views.MethodView):

    def get(self, message=None):
        # 渲染具有层级目录的书写方法
        return render_template('cms/cms_login.html', message=message)

    def post(self):
        # 将页面提交的数据导入 wtforms 进行验证
        form = LoginForm(request.form)

        email = form.email.data
        password = form.password.data
        remember = form.remember.data

        if form.validate():
            user = CMSUser.query.filter_by(email=email).first()
            if user and user.check_password(password):

                session[config.CMS_USER_ID] = user.id

                # 对应页面的 remember me 功能
                # 如果设置 session.permanet = True，那么过期时间是 31天
                if remember:
                    session.permanent = True

                # 蓝图使用 url_for ，记得把蓝图的名字给加上。
                # 使用 url_for 反转蓝图的普通视图函数
                return redirect(url_for('cms.index'))
            else:
                return self.get(message='邮箱或者密码错误')
                # return render_template('/cms/cms_login.html', message='邮箱或者密码错误')

        else:
            # 返回具体的错误验证信息
            # form.errors : {'password': ['请输入正确格式的密码']}
            message = form.errors.popitem()[1][0]
            # 表单验证错误（数据格式不对）
            return self.get(message=message)
            # return render_template('/cms/cms_login.html',message='表单验证错误（数据格式不对）')


# 基于调度方法的类视图和蓝图的结合使用（以前一直以为自己不会的东西）
# 特别注意这有个东西，as_view ，给 view_func 起个名字，相当于非类写法里面的视图函数
cms_bp.add_url_rule('/login/', view_func=LoginView.as_view('login'))






















