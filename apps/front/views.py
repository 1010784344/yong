# -*- coding: utf-8 -*-
# from apps.front import bp
import os
import shortuuid
from flask import Blueprint,views,render_template,request,jsonify,session,url_for,g,abort
from apps.front.forms import SignupForm,SigninForm,AddPostForm,AddCommentForm
from apps.models import BannersModel,BoardModel,PostModel,CommentModel,HighlightPostModel,TaskModel,WorkModel,PortModel,HostModel
from apps.front.models import FrontUser
from apps.front.decorators import LoginRequired
from exts import alidayu,db,mydocker
from utils import safeutils
import config
from flask_paginate import Pagination,get_page_parameter
from tasks import create_contest
import redis
redisex = redis.Redis(host='127.0.0.1', port=6379, db=0)

from sqlalchemy import func

front_bp = Blueprint('front', __name__)

# 测试：注册完成跳转回上一个页面
@front_bp.route('/test/')
def test():
    return render_template('test.html')


@front_bp.route('/')
def index():
    # 轮播图展示
    banners = BannersModel.query.order_by(BannersModel.priority.desc()).limit(4)
    boards = BoardModel.query.all()

    # 排序信息(当没有st赋值，默认为 1 ，也就是当为首页时，st=1)
    st = request.args.get('st',type=int,default=1)

    # 分页前
    # posts = PostModel.query.all()

    # 分页后
    # 从 url 的查询参数获取当前是第几页(指定当前是第几页)
    page = request.args.get(get_page_parameter(),type=int,default=1)

    start = (page-1)*config.PER_PAGE
    end = start + config.PER_PAGE

    # 选中的板块
    bd = request.args.get('bd', type=int, default=None)
    total = 0
    query_obj = None

    # 最新帖排序
    if st == 1:
        query_obj = TaskModel.query.order_by(TaskModel.creat_time.desc())
    # 精华帖排序(左连接)
    # if st == 2:
    #     query_obj = db.session.query(PostModel).outerjoin(HighlightPostModel).order_by(HighlightPostModel.create_time.desc(),PostModel.create_time.desc())
    # # 点赞最多排序（功能还没有实现，暂时跟最新帖是一样的）
    # if st == 3:
    #     query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    # # 评论最多排序
    # if st == 4:
    #     # 按一个帖子下面评论的多少来给这些帖子进行排序
    #     # 先把评论按帖子来进行分组，然后再根据评论的个数进行排序（需要多多进行学习）
    #     query_obj = db.session.query(PostModel).outerjoin(CommentModel).group_by(PostModel.id).\
    #         order_by(func.count(CommentModel.id).desc(), PostModel.create_time.desc())

    # 获取指定页的数据
    if bd:
        posts = query_obj.filter(PostModel.board_id == bd).slice(start,end)
        total = query_obj.filter(PostModel.board_id == bd).count()
    else:
        posts = query_obj.slice(start, end)
        total = query_obj.count()

    # pagination 用于前台页面的上一页和下一页的控制
    pagination = Pagination(bs_version=3, page=page,total=total)


    # 返回多个参数到 html 页面
    context = {'banners':banners,
               'boards': boards,
               'posts': posts,
               'pagination':pagination,
               # 方便前端点击那个板块，那个板块就选中的参数
               'current_board':bd,
               'current_st':st

               }


    return render_template('front/front_index.html',**context)


# 测试：短信验证测试接口(其他方面都正常，就接口有问题（appkey-not-exists），暂时放过)
# 阿里云账号：ali1010784344   密码：cwx364505

@front_bp.route('/sms_captcha/')
def sms_captcha():
    result = alidayu.send_sms('18735934287',code='abcd')
    if result:
        print('发送成功')
    else:
        print('发送失败')


# 发布帖子
@front_bp.route('/apost/',methods=['GET','POST'])
@LoginRequired
def apost():

    if request.method == 'GET':
        boards = BoardModel.query.all()
        return render_template('front/front_apost.html',boards=boards)
    else:
        form = AddPostForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data


            board = BoardModel.query.get(board_id)


            if not board:
                return jsonify({'code': '400', 'message': '没有这个板块！'})
            else:
                post = PostModel(title=title,content=content)
                post.boards = board
                # 帖子新增用户名
                post.author = g.front_user

                db.session.add(post)
                db.session.commit()

                return jsonify({'code': '200', 'message': '帖子发布成功！'})

        else:
            message = form.errors.popitem()[1][0]
            # 表单验证错误（数据格式不对）

            return jsonify({'code': '400', 'message': message})



# 创建赛题
# @front_bp.route('/acontest/',methods=['GET','POST'])
# @LoginRequired
# def acontest():
#
#     if request.method == 'GET':
#         boards = BoardModel.query.all()
#         return render_template('front/front_apost.html',boards=boards)
#     else:
#         form = AddPostForm(request.form)
#         if form.validate():
#             title = form.title.data
#             content = form.content.data
#             board_id = form.board_id.data
#
#
#             board = BoardModel.query.get(board_id)
#
#
#             if not board:
#                 return jsonify({'code': '400', 'message': '没有这个板块！'})
#             else:
#                 post = PostModel(title=title,content=content)
#                 post.boards = board
#                 # 帖子新增用户名
#                 post.author = g.front_user
#
#                 db.session.add(post)
#                 db.session.commit()
#
#                 return jsonify({'code': '200', 'message': '帖子发布成功！'})
#
#         else:
#             message = form.errors.popitem()[1][0]
#             # 表单验证错误（数据格式不对）
#
#             return jsonify({'code': '400', 'message': message})







# 帖子详情
@front_bp.route('/p/<post_id>/')
def post_detail(post_id):
    post = PostModel.query.get(post_id)

    if not post:
        #如果帖子不存在，手动抛出一个异常
        abort(404)
    else:
        return render_template('front/front_pdetail.html',post=post)


# 任务详情
@front_bp.route('/t/<post_id>/')
def task_detail(post_id):
    post = TaskModel.query.get(post_id)

    if not post:
        #如果帖子不存在，手动抛出一个异常
        abort(404)
    else:
        return render_template('front/front_tdetail.html',post=post)



# 发表评论
@front_bp.route('/acomment/',methods=['POST'])
@LoginRequired
def acomment():

    form = AddCommentForm(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data

        post = PostModel.query.get(post_id)

        if not post:
            return jsonify({'code': '400', 'message': '没有这个帖子！'})
        else:
            comment = CommentModel(content=content)
            comment.posts = post
            comment.author = g.front_user

            db.session.add(comment)
            db.session.commit()

            return jsonify({'code': '200', 'message': '帖子发布成功！'})

    else:
        message = form.errors.popitem()[1][0]
        # 表单验证错误（数据格式不对）

        return jsonify({'code': '400', 'message': message})

# 创建任务
@front_bp.route('/acontest/<uuid>',methods=['GET'])
# @front_bp.route('/acontest/',methods=['GET'])
@LoginRequired
def acontest(uuid):
    # uuid = 'hakulamatata'
    task_id = request.args.get("task_id")

    task = TaskModel.query.get(task_id)


    if not task:
        return jsonify({'code': '400', 'message': '没有这个赛题！'})
    else:
        # 一个人一次只能做一道题，之前做到一半的题就会结束，做这道题，就会把上一道题干掉
        # user_id = g.front_user.id
        # works = WorkModel.query.filter_by(task_status=1).all()
        #
        # if not works:
        #     work = WorkModel(task_flag='11111')
        # elif len(works) == 1:
        # #如果只有一个，那就停止并重新创建
        #
        #     pass
        # else:
        #     return jsonify({'code': '400', 'message': '创建失败！'})




        work = WorkModel(task_flag='11111',author_id=g.front_user.id)

        if task.type == 'dynamic':

            taskflag = shortuuid.uuid()[:4]
            work.task_flag = taskflag

        work.tasks = task

        work.writer = g.front_user
        # work.id = uuid
        from sqlalchemy import func
        host = db.session.query(HostModel).order_by(func.count(HostModel.works)).first()
        # len(HostModel.works)
        # 获取空闲的主机
        # host = HostModel.query.filter_by(status='1').first()
        tmpip = host.ip
        tmphost = host.name
        # work.hosts = host
        # 获取空闲的端口号
        if tmphost == 'host1':
            # 获取空闲的端口号
            port = PortModel.query.filter_by(host1='5').first()
            tmpport = port.name
            port.host1 = "10"
        elif tmphost == 'host2':
            # 获取空闲的端口号
            port = PortModel.query.filter_by(host2='5').first()
            tmpport = port.name
            port.host2 = "10"

        # work.hostport = '192.168.141.177:%s'%tmpport
        work.hostport = '%s:%s'%(tmpip,tmpport)
        work.task_status = '1'
        # 容器创建完毕之后，修改port 的状态
        # port.status = "10"
        # 异步启动创建流程
        create_contest.delay(uuid,task.name,task.image,port.name,taskflag)
        """
        
        """

        # import redis
        #
        # redisex = redis.Redis(host='127.0.0.1', port=6379, db=0)
        # redisex.hset(work.id, 'progress',0)
        #
        #
        #
        #
        # # tar包 转移到对应的机器（有可能跨机器暂未实现）
        # taskpath = os.path.join(config.UPLOADED_dir, task.name+os.sep+task.image)
        # import shutil
        # tmppath = '/home/srv'
        # # 本地 tar 包目录
        # realpath = tmppath + os.sep + task.image
        # if not os.path.exists(realpath):
        #     shutil.copy(taskpath,tmppath)
        #
        # redisex.hset(work.id, 'progress', 20)
        #
        # try:
        #     # 检查 nginx 镜像是否存在（反向代理必须要有的镜像）
        #     img = mydocker.images.get("nginx")
        #     imagename = img.tags[0].split(':')[0]
        # except Exception as e:
        #     # 加载镜像
        #     with open(realpath, 'rb') as fp:
        #         img = mydocker.images.load(fp.read())
        #         # 获取镜像名称
        #     imagename = img[0].tags
        # redisex.hset(work.id, 'progress', 40)


        # imagename = 'nginx'

        # 创建代理容器
        """
        
        
        
        """


        # 赛题创建容器
        # tmpdocker = mydocker.containers.run(imagename, name=tmpname,ports= {'80/tcp': ('192.168.141.177', tmpport)}, tty=True,detach=True)
        #

        # import shortuuid
        # tmpuuid = shortuuid.uuid()
        # redisex.hset(work.id, 'progress', 60)
        #
        #
        #
        # # 配置代理配置文件
        # confinfo = config.CONF_info%(tmpuuid,tmpport)
        # f = open("/home/wang/nginx/conf.d/%s.conf"%tmpname,"w")
        # f.write(confinfo)
        # f.close()
        #
        # redisex.hset(work.id, 'progress', 80)
        # # 获取代理容器并再代理容器重新加载 nginx 配置文件
        # pro = mydocker.containers.get("proxy-ng")
        # pro.exec_run("nginx -s reload")
        # redisex.hset(work.id, 'progress', 100)
        # redisex.hset(work.id, 'domain', '%s.testnginx.com' % tmpuuid)


        db.session.add(work)
        db.session.commit()


        return jsonify({'code': '200', 'message': '成功！'})


# 删除任务
@front_bp.route('/dcontest/', methods=['GET'])
@LoginRequired
def dcontest():
    task_id = request.args.get("task_id")

    task = TaskModel.query.get(task_id)

    if not task:
        return jsonify({'code': '400', 'message': '没有这个赛题！'})
    else:
        # 容器名称就是赛题名称
        user_id = g.front_user.id
        work = WorkModel.query.filter_by(task_id=task_id,author_id=user_id).first()
        work.task_status = 2
        tmpname = task.name
        tmpport = work.hostport.split(':')[1]

        tmpip = work.hostport.split(':')[0]

        if tmpip == '192.168.141.177':
            # 将端口号设置为空闲状态
            port = PortModel.query.filter_by(name=tmpport).first()
            port.host1 = '5'
        elif tmpip == '192.168.141.178':
            # 将端口号设置为空闲状态
            port = PortModel.query.filter_by(name=tmpport).first()
            port.host2 = '5'

        import redis

        redisex = redis.Redis(host='127.0.0.1', port=6379, db=0)
        redisex.hdel(work.id, 'progress')
        redisex.hdel(work.id, 'domain')


        # 获取赛题容器
        tmpdocker = mydocker.containers.get(tmpname)
        tmpdocker.remove(force=True)

        confpath = "/home/wang/nginx/conf.d/%s.conf" % tmpname
        if os.path.exists(confpath):
            os.remove(confpath)

        pro = mydocker.containers.get("proxy-ng")
        pro.exec_run("nginx -s reload")


        db.session.add(work)
        db.session.commit()

        return jsonify({'res': '200', 'message': '成功！'})


@front_bp.route('/progress_data/<uuid>')
def progress_data(uuid):
    '''
    通过uuid将数据存入变量progress_data
    '''
    while True:
        tmpdata = redisex.hget(uuid, 'progress')
        if tmpdata == '100':
            break
    domain = redisex.hget(uuid, 'domain')

    return jsonify({'res': tmpdata,'domains':domain})

@front_bp.route('/show_progress/<uuid>')
def show_progress(uuid):
    '''
    前端请求进度的函数
    '''
    try:
        tmpdata = redisex.hget(uuid, 'progress')
    except Exception as e:
        tmpdata = 0


    return jsonify({'res': tmpdata})



class SignupView(views.MethodView):

    def get(self):
        # 获取上一个页面的 url
        return_to = request.referrer
        if return_to and return_to != request.url and safeutils.is_safe_url(return_to):
            return render_template('front/front_signup.html',return_to=return_to)
        else:
            return render_template('front/front_signup.html')
    def post(self):
        form = SignupForm(request.form)

        if form.validate():
            # telephone = form.telephone.data
            username = form.username.data
            password = form.password.data
            user = FrontUser(username=username,password=password)
            db.session.add(user)
            db.session.commit()

            return jsonify({'code': '200', 'message': '用户注册成功！'})
        else:

            message = form.errors.popitem()[1][0]
            # 表单验证错误（数据格式不对）

            return jsonify({'code': '400', 'message': message})


class SigninView(views.MethodView):

    def get(self):
        # 获取上一个页面的 url
        return_to = request.referrer
        # 不能跳转到本页面及注册页面
        if return_to and return_to != request.url and return_to != url_for('front.signup') and safeutils.is_safe_url(return_to):
            return render_template('front/front_signin.html',return_to=return_to)
        else:
            return render_template('front/front_signin.html')

    def post(self):
        form = SigninForm(request.form)
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







front_bp.add_url_rule('/signup/',view_func=SignupView.as_view('signup'))
front_bp.add_url_rule('/signin/',view_func=SigninView.as_view('signin'))
