from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user
from flask import render_template
from .import auth
from ..models import User
from .forms import LoginForm,RegistrationForm
from flask_login import login_required, logout_user, current_user
from .. import db
from ..email import send_email
'''
当请求类型是 GET 时，视图函数直接渲染模板，即显示表单。当表单在 POST 请求中提交时，
Flask-WTF 中的 validate_on_submit() 函数会验证表单数据，然后尝试登入用户。
'''

'''
在生产服务器上，登录路由必须使用安全的 HTTP，从而加密传送给服务器
的表单数据。如果没使用安全的 HTTP，登录密令在传输过程中可能会被截
取，在服务器上花再多的精力用于保证密码安全都无济于事。
'''
'''
为了登出用户，这个视图函数调用 Flask-Login 中的 logout_user() 函数，删除并重设用户
会话。随后会显示一个 Flash 消息，确认这次操作，再重定向到首页，这样登出就完成了。
'''


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

'''
如果未认证的用户访问这个路由，Flask-Login 会拦截请求，把用户发往登录页面
'''


@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed'


'''
注意，即便通过配置，程序已经可以在请求末尾自动提交数据库变化，这里也要添加
db.session.commit() 调用。问题在于，提交数据库之后才能赋予新用户 id 值，而确认令
牌需要用到 id ，所以不能延后提交
'''
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        #flash('You can now login.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

'''
确认邮件中最简单的确认链接是 http://www.example.com/auth/confirm/<id> 这种形式的
URL，其中 id 是数据库分配给用户的数字 id 。用户点击链接后，处理这个路由的视图函
数就将收到的用户 id 作为参数进行确认，然后将用户状态更新为已确认。

但这种实现方式显然不是很安全，只要用户能判断确认链接的格式，就可以随便指定 URL
中的数字，从而确认任意账户。解决方法是把 URL 中的 id 换成将相同信息安全加密后得
到的令牌。
'''

'''
用户点击确认邮件中的链接后，要先登录，然后才能执行这个视图函数。
这个函数先检查已登录的用户是否已经确认过，如果确认过，则重定向到首页，
因为很显然此时不用做什么操作。这样处理可以避免用户不小心多次点击确认令牌带来的额外工作。
由于令牌确认完全在 User 模型中完成，所以视图函数只需调用 confirm() 方法即可，
然后再根据确认结果显示不同的 Flash 消息。确认成功后，
User 模型中 confirmed 属性的值会被修改并添加到会话中，
请求处理完后，这两个操作被提交到数据库。
'''


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

'''
每个程序都可以决定用户确认账户之前可以做哪些操作。比如，允许未确认的用户登录，
但只显示一个页面，这个页面要求用户在获取权限之前先确认账户。
对蓝本来说， before_request 钩子只能应用到属于蓝本的请求上。若想在
蓝本中使用针对程序全局请求的钩子，必须使用 before_app_request 修饰器。
'''

'''
(1) 用户已登录（ current_user.is_authenticated() 必须返回 True ）。
(2) 用户的账户还未确认。
(3) 请求的端点（使用 request.endpoint 获取）不在认证蓝本中。访问认证路由要获取权
限，因为这些路由的作用是让用户确认账户或执行其他账户管理操作。
如果请求满足以上 3 个条件，则会被重定向到 /auth/unconfirmed 路由，显示一个确认账户
相关信息的页面。
'''


@auth.before_app_request
def before_request():
    if current_user.is_authenticated() \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.'\
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))