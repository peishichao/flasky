from datetime import datetime
from flask import render_template,session,redirect,url_for
from . import main
from . forms import NameForm
from .. import db
from .. models import User
'''
在蓝本中编写视图函数主要有两点不同：第一，和前面的错误处理程序一样，路由修饰器
由蓝本提供；第二， url_for() 函数的用法不同。你可能还记得， url_for() 函数的第一
个参数是路由的端点名，在程序的路由中，默认为视图函数的名字。例如，在单脚本程序
中， index() 视图函数的 URL 可使用 url_for('index') 获取。
在蓝本中就不一样了，Flask 会为蓝本中的全部端点加上一个命名空间，这样就可以在不
同的蓝本中使用相同的端点名定义视图函数，而不会产生冲突。命名空间就是蓝本的名字
（ Blueprint 构造函数的第一个参数），所以视图函数 index() 注册的端点名是 main.index ，
其 URL 使用 url_for('main.index') 获取。
url_for() 函数还支持一种简写的端点形式，在蓝本中可以省略蓝本名，例如 url_for('.
index') 。在这种写法中，命名空间是当前请求所在的蓝本。这意味着同一蓝本中的重定向
可以使用简写形式，但跨蓝本的重定向必须使用带有命名空间的端点名。
'''




@main.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        #name = form.name.data
        #old_name = session.get('name')
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        #return redirect(url_for('index'))
        #if old_name is not None and old_name != form.name.data:
        #    flash('Looks like you have changed your name!')
        #session['name'] = form.name.data
        #form.name.data = ''
        #redirect()函数用来生成HTTP重定向响应，redirect函数的参数是重定向的URL
        #url_for函数的第一个且唯一必须制定的参数端点名，即路由的内部名称
        #路由的端点是响应视图函数的名称
        #使用session.get的方式可以避免找不到键值的情况
        return redirect(url_for('.index'))
    return render_template('index.html', form=form, name=session.get('name'), known = session.get('known',False), current_time=datetime.utcnow())
    #user_agent = request.headers.get('User-Agent')
    #return render_template('index.html', current_time=datetime.utcnow())
    #return '<h1>hello worlds!</h1>'