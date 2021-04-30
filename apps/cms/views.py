# -*- coding: utf-8 -*-
from flask import Blueprint,render_template,views,request,redirect,url_for,session,g,jsonify
from apps.cms.forms import LoginForm,ResetpwdForm,ResetemailForm,AddBannerForm,UpdateBannerForm,AddBoardForm,UpdateBoardForm
from apps.cms.models import CMSUser,CMPermission
from apps.models import BannersModel,BoardModel,PostModel,HighlightPostModel
import config
from apps.cms.decorators import LoginRequired,permission_required
from exts import db,mail
from utils import zlmemcache
from flask_mail import Message
import string
import random
from tasks import send_email

# 定义 cms 的蓝图
cms_bp = Blueprint('cms',__name__,url_prefix='/cms')

# cms 首页
@cms_bp.route('/index/')
@LoginRequired
def index():
    return render_template('/cms/cms_index.html')

# cms 注销
@cms_bp.route('/logout/')
@LoginRequired
def logout():
    session.pop(config.CMS_USER_ID)
    return redirect(url_for('cms.login'))


# cms 个人中心
@cms_bp.route('/profile/')
@LoginRequired
def profile():

    return render_template('cms/cms_profile.html')


# cms 给指定邮箱发送验证码（ajax 调用）
@cms_bp.route('/sendcaptcha/')
def sendcaptcha():

    #/cms/sendcaptcha/?email=1010784344@qq.com

    # 获取邮箱（给谁发）
    email = request.args.get('email')
    if not email:
        return jsonify({'code': '400', 'message': '请输入邮箱！'})
    else:


        # 获取验证码（内容）
        allcaptcha = list(string.ascii_letters)
        allcaptcha.extend(map(lambda x:str(x),range(0,10)))
        captcha = ''.join(random.sample(allcaptcha,6))

        print(email,captcha)

        # 储存验证码到内存中（memcached）
        zlmemcache.set(email,captcha)

        #发送验证码

        # # celery异步前
        # message = Message('王者荣耀论坛邮箱验证码', recipients=[email], body='您的邮箱验证码是：%s'%captcha)
        # try:
        #     mail.send(message)
        # except:
        #     return jsonify({'code': '400', 'message': '网络错误！'})

        # celery异步后触发任务
        send_email.delay('王者荣耀论坛邮箱验证码', recipients=[email], body='您的邮箱验证码是：%s' % captcha)


        return jsonify({'code': '200', 'message': '验证码已经发送至您的邮箱，请确认！'})



# 发送邮件测试
@cms_bp.route('/emailbug/')
def emailbug():
    # 邮件主题，收件人列表，邮件正文
    message = Message('邮件发送',recipients=['1010784344@qq.com'],body='测试')
    mail.send(message)
    return 'success'


# 轮播图管理（这里就不添加权限验证了）
@cms_bp.route('/banners/')
@LoginRequired
def banners():

    # allbanner = BannersModel.query.all()
    # 按照权重倒叙排列
    allbanner = BannersModel.query.order_by(BannersModel.priority.desc()).all()

    return render_template('cms/cms_banners.html',allbanner=allbanner)



#添加轮播图弹窗 的提交表单
@cms_bp.route('/abanner/',methods = ['POST'])
@LoginRequired
def abanner():

    form = AddBannerForm(request.form)

    if form.validate():
        name = form.name.data
        img_url = form.img_url.data
        link_url = form.link_url.data
        priority = form.priority.data

        banner = BannersModel(name=name, image_url=img_url,link_url=link_url, priority=priority)

        db.session.add(banner)
        db.session.commit()

        return jsonify({'code': '200', 'message': '轮播图添加成功！'})
    else:

        message = form.errors.popitem()[1][0]
        # 表单验证错误（数据格式不对）

        return jsonify({'code': '400', 'message': message})




#编辑轮播图弹窗 的提交表单
@cms_bp.route('/ubanner/',methods = ['POST'])
@LoginRequired
def ubanner():

    form = UpdateBannerForm(request.form)

    if form.validate():
        name = form.name.data
        img_url = form.img_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        bannerid = form.banner_id.data

        banner = BannersModel.query.get(bannerid)

        if banner:
            banner.name = name
            banner.img_url = img_url
            banner.link_url = link_url
            banner.priority = priority

            # db.session.add(banner)
            db.session.commit()

            return jsonify({'code': '200', 'message': '轮播图编辑成功！'})
        else:
            return jsonify({'code': '400', 'message': '轮播图不存在！'})
    else:

        message = form.errors.popitem()[1][0]
        # 表单验证错误（数据格式不对）

        return jsonify({'code': '400', 'message': message})


#删除轮播图弹窗 的提交表单
@cms_bp.route('/dbanner/',methods = ['POST'])
@LoginRequired
def dbanner():

    bannerid = request.form.get('banner_id')

    if not bannerid:
        return jsonify({'code': '400', 'message': '轮播图id不存在！'})


    banner = BannersModel.query.get(bannerid)
    if not banner:
        return jsonify({'code': '400', 'message': '轮播图不存在！'})


    db.session.delete(banner)
    db.session.commit()
    return jsonify({'code': '200', 'message': '轮播图删除成功！'})





# 帖子管理
@cms_bp.route('/posts/')
@LoginRequired
@permission_required(CMPermission.POSTER)
def posts():
    all_post = PostModel.query.all()
    return render_template('cms/cms_posts.html',all_post=all_post)


# 帖子加精
@cms_bp.route('/hpost/',methods = ['POST'])
@LoginRequired
@permission_required(CMPermission.POSTER)
def hpost():

    # post_id = request.args.get('post_id')
    post_id = request.form.get('post_id')

    if not post_id:
        return jsonify({'code': '400', 'message': '请输入帖子id！'})

    post = PostModel.query.get(post_id)

    if not post:
        return jsonify({'code': '400', 'message': '帖子不存在！'})

    highlight = HighlightPostModel()
    highlight.posts = post

    db.session.add(highlight)
    db.session.commit()

    return jsonify({'code': '200', 'message': '帖子加精成功！'})



# 帖子取消加精
@cms_bp.route('/uhpost/',methods = ['POST'])
@LoginRequired
@permission_required(CMPermission.POSTER)
def uhpost():

    post_id = request.form.get('post_id')

    if not post_id:
        return jsonify({'code': '400', 'message': '请输入帖子id！'})

    # 帖子取消加精，这里其实并没有用到 post 这个对象，只是用这个对象去看帖子是否存在而已
    post = PostModel.query.get(post_id)
    if not post:
        return jsonify({'code': '400', 'message': '帖子不存在！'})

    highlight = HighlightPostModel.query.filter_by(post_id=post_id).first()

    db.session.delete(highlight)
    db.session.commit()

    return jsonify({'code': '200', 'message': '帖子取消加精成功！'})









# 评论管理
@cms_bp.route('/comments/')
@LoginRequired
@permission_required(CMPermission.COMMENTER)
def comments():
    return render_template('cms/cms_comments.html')



# 板块管理
@cms_bp.route('/boards/')
@LoginRequired
@permission_required(CMPermission.BOARDER)
def boards():
    all_boards = BoardModel.query.all()
    return render_template('cms/cms_boards.html',boards = all_boards)


# 添加板块
@cms_bp.route('/aboards/', methods=['POST'])
@LoginRequired
@permission_required(CMPermission.BOARDER)
def aboards():

    form = AddBoardForm(request.form)

    if form.validate():
        name = form.name.data

        board = BoardModel(name=name)

        db.session.add(board)
        db.session.commit()

        return jsonify({'code': '200', 'message': '板块添加成功！'})
    else:

        # 表单验证错误（数据格式不对）
        message = form.errors.popitem()[1][0]

        return jsonify({'code': '400', 'message': message})



# 更新板块
@cms_bp.route('/uboards/', methods=['POST'])
@LoginRequired
@permission_required(CMPermission.BOARDER)
def uboards():

    form = UpdateBoardForm(request.form)

    if form.validate():
        name = form.name.data
        boardid = form.board_id.data

        banner = BannersModel.query.get(boardid)

        if banner:
            banner.name = name

            db.session.commit()

            return jsonify({'code': '200', 'message': '板块编辑成功！'})
        else:
            return jsonify({'code': '400', 'message': '板块不存在！'})
    else:
        # 表单验证错误（数据格式不对）
        message = form.errors.popitem()[1][0]

        return jsonify({'code': '400', 'message': message})




# 删除板块
@cms_bp.route('/dboards/', methods=['POST'])
@LoginRequired
@permission_required(CMPermission.BOARDER)
def dboards():

    # 没有经过验证直接获取数据的方式
    boardid = request.form.get('board_id')

    if not boardid:
        return jsonify({'code': '400', 'message': '板块id不存在！'})

    # board = BoardModel.query.filter_by(id=boardid).first()
    board = BoardModel.query.get(boardid)

    if not board:
        return jsonify({'code': '400', 'message': '板块不存在！'})

    db.session.delete(board)
    db.session.commit()
    return jsonify({'code': '200', 'message': '板块删除成功！'})


# 前台用户管理
@cms_bp.route('/fusers/')
@LoginRequired
@permission_required(CMPermission.FRONTUSER)
def fusers():
    return render_template('cms/cms_fusers.html')



# CMS用户管理
@cms_bp.route('/cusers/')
@LoginRequired
@permission_required(CMPermission.CMSUSER)
def cusers():
    return render_template('cms/cms_cusers.html')




# CMS组管理
@cms_bp.route('/croles/')
@LoginRequired
@permission_required(CMPermission.ALL_PERMISSION)
def croles():
    return render_template('cms/cms_croles.html')




# cms 登录
# 基于调度方法的类视图
class Login_View(views.MethodView):
    def get(self,message=None):
        # 渲染具有层级目录的书写方法
        return render_template('cms/cms_login.html',message=message)
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


# cms 修改密码
class ResetPwd_View(views.MethodView):

    # 基于调度方法添加装饰器
    decorators = [LoginRequired]

    def get(self):
        # 渲染具有层级目录的书写方法
        return render_template('/cms/cms_resetpwd.html')
    def post(self):
        # 将页面提交的数据导入 wtforms 进行验证
        form = ResetpwdForm(request.form)

        if form.validate():

            oldpwd = form.oldpwd.data
            newpwd = form.newpwd.data
            print(oldpwd)
            # 这个就不需要获取了，因为关于和新密码不一致的问题，
            # forms.py 里面的 wt-form 验证器已经帮我们验证过了
            # newpwd2 = form.newpwd2.data

            # user 对象在钩子函数里面已经提前获取过了
            user = g.cms_user

            if user.check_password(oldpwd):
                user.password = newpwd
                db.session.commit()

                # 返回json数据
                return jsonify({'code': '200', 'message': '密码修改成功！'})
            else:
                return jsonify({'code':'400','message':'旧密码输入错误！'})
        else:
            # 返回具体的错误验证信息
            # form.errors : {'password': ['请输入正确格式的密码']}
            message = form.errors.popitem()[1][0]
            # 表单验证错误（数据格式不对）

            return jsonify({'code': '400', 'message': message})

# cms 修改邮箱
class ResetEmail_View(views.MethodView):

    # 基于调度方法添加装饰器
    decorators = [LoginRequired]

    def get(self):
        return render_template('/cms/cms_resetemail.html')

    def post(self):
        # 将页面提交的数据导入 wtforms 进行验证
        form = ResetemailForm(request.form)

        # 因为数据已经验证过了，我们只需要将数据修改就行了
        if form.validate():

            email = form.email.data
            user = g.cms_user
            user.email = email
            db.session.commit()
            return jsonify({'code': '200', 'message': '邮箱修改成功！'})
        else:
            # 返回具体的错误验证信息
            message = form.errors.popitem()[1][0]
            return jsonify({'code': '400', 'message': message})

# 基于调度方法的类视图和蓝图的结合使用（以前一直以为自己不会的东西）
# 特别注意这有个东西，as_view ，给 view_func 起个名字，相当于非类写法里面的视图函数
cms_bp.add_url_rule('/login/',view_func=Login_View.as_view('login'))
cms_bp.add_url_rule('/resetpwd/',view_func=ResetPwd_View.as_view('resetpwd'))
cms_bp.add_url_rule('/resetemail/',view_func=ResetEmail_View.as_view('resetemail'))





















