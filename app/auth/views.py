from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user
from flask import render_template
from .import auth
from ..models import User
from .forms import LoginForm
from flask_login import login_required

'''
当请求类型是 GET 时，视图函数直接渲染模板，即显示表单。当表单在 POST 请求中提交时，
Flask-WTF 中的 validate_on_submit() 函数会验证表单数据，然后尝试登入用户。
'''


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