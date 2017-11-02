from datetime import datetime
from flask import Flask
from flask import request
from flask import session
from flask import url_for, redirect, flash
from flask import render_template
from flask_script import Manager
#from hello import app
#app.url_map
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread



'''
每次启动shell会话都要导入数据库实例和模型
为了避免一直重复导入，自动导入特定的对象
'''
import os





class NameForm(FlaskForm):
    name = StringField('what is your name?', validators=[DataRequired()])
    submit = SubmitField('submit')

'''
Flask提供的render_template函数把Jinja2模板引擎集成了程序中
render_template函数的第一个参数是模板的文件名
随后的参数都是键值对，表示模板中变量对应的真实值
左边的表示的是参数名，模板中的占位符
右边的表示当前作用域的变量，表示同名参数的值
Jinja2能够识别所有类型的变量，甚至是一些复杂的类型
例如：列表，字典和对象
{{mydict['key']}}
{{mylist[3]}}
myobj.somemethod()
还可以使用过滤器修改变量，过滤器名添加在变量名之后，中间使用竖线分割
hello.{{name|capitalize}}
以首字母大写形式显示变量name的值
Jinja2变量过滤器：

safe 渲染值时不转义
如果变量的值为：<h1>hello</h1>，如果想理解<h1>那么就需要safe
**：千万不可以在用户的表单上面使用safe过滤器
capitalize 把值得首字母转换为大写，其他字母转化为小写
lower 把值转化为小写
upper
title 把值中的每个单词的首字母都转化为大写
trim 把值得首尾空格去掉
striptags 渲染之前把值中所有的HTML标签都删掉
'''

'''
Map([<Rule '/' (HEAD, OPTIONS, GET) -> index>,
<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
大多数程序还会使用静态文件
static路由信息
静态文件的引用被当成一个特殊的路由 /static/<filename>
url_for('static',filename='css/styles.css',_external=True)
得到的结果是http://localhost:5000/static/css/styles.css
<Rule '/user/<name>' (HEAD, OPTIONS, GET) -> user>])

/static/<filename>路由是Flask添加的特殊路由，用于访问静态文件
(HEAD, OPTIONS, GET)是请求方法，由路由进行处理

请求钩子使用修饰器实现，Flask支持下面4中钩子
before_first_request 在处理第一个请求之前运行
before_request 在每次请求之前运行
after_request 没有没处理的异常抛出，请求之后运行
teardown_request 即使有异常也在每次请求之后运行
请求钩子函数和视图函数之间共享数据一般使用上下文全局变量g
'''
from flask import current_app


#直接使用报错，需要激活
#current_app.name
#使用之前需要先推送
#app_ctx = app.app_context()||调用该方法获得一个程序上下文
#app_ctx.push()
#current_app.name

#在每个视图函数中我们将request视为全局变量使用，实际上request不可能为全局变量，在多线程服务器中，
#多个线程同时处理不同客户端发送的不同请求，每个线程看到的request必然不同，Flask使用上下文让特定的变量
#在一个线程中全局可访问，于此同时却不干扰其他线程


#激活或者推送程序和请求上下文
#Flask有两种上下文：程序上下文和请求上下文
#current_app,g,程序上下文||request,session,请求上下文

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)
#SECRET_KEY配置变量时通用秘钥，可以在多方扩展中使用
#为了增强安全性，秘钥不应该直接写入代码，而要保存在环境变量中
app.config['SECRET_KEY'] = 'dfvdf@#$HKUIyibb'
'''
千万不要把账号秘钥直接写入脚本，特别是当你计划开源你自己的作品的时候，
为了保护账号信息，你需要让脚本从环境中导入敏感信息

环境变量中获取邮件服务器用户名和密码
ubuntu$export MAIL_USERNAME = <Gmail username>
windows$set MAIL_USERNAME = <Gmail username>
'''
app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
#Email

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'#邮件主题的前缀
app.config['FLASKY_MAIL_SENDER'] = '15630965489@163.com'#发件人地址
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(to,subject,template,**kwargs):#收件人地址，主题，渲染模板，关键字参数
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt',**kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr

def make_shell_context():
        return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell",Shell(make_context=make_shell_context))
'''
Model
'''
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' %self.name
'''
__tablename__ 定义在数据库中使用的表名
如果没有定义__tablename__，会使用一个默认名字，但是不遵循复数形式进行命名的约定
属性：db.Column

Flask-SQLAlchemy要求每个模型都要定义主键，这一列经常命名为ID


db.create_all()
db.drop_all()

admin_role = Role(name='Admin')
##admin_role.name = 'Administrator'
mod_role = Role(name='Moderator')
user_role = Role(name='User')
user_john = User(username='john',role=admin_role)
通过数据库绘画管理对数据库所做的相关改动，会话由db.session表示
db.session.add(admin_role)
db.session.add(...)
db.session.delete(mod_role)
#插入和更新一样， 提交数据库会话后才能够执行
db.session.add_all([amin_role,...])
db.session.commit()

数据库会话能够保证数据库的一致性，提交操作使用原子操作会把会话中的对象全部写入数据库
如果写入过程中发生错误，整个会话失效，

数据库会话也可以回滚，条用db.session.rollback()，添加到数据库会话中的所有对象都会还原到他们在数据库中的状态


查询：
Role.query.all()
User.query.all()

User.query.filter_by(role=user_role).all()::查找角色为User的所有用户

查看原生SQL语句
str(User.query.filter_by(role=user_role).all())

user_role = Role.query.filter_by(name='User').first()

通过all()执行查询，以列表的形式返回结果
'''
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<User %r>' %self.username







'''
url_for()函数最简单的用法是以视图函数名作为参数，返回对应的URL
例如：调用url_for('index')得到的结果是/
调用url_for('index',_external=True)返回的是绝对地址，如实例中为http://localhost:5000/

如果生成连接程序内不同路由的链接时，使用相对地址就足够了，
如果生成浏览器之外使用的连接，必须使用绝对地址，
使用url_for()生成动态地址的时候，将动态部分作为关键字的参数传入
url_for('user',name='peishichao',_external=True)
返回结果为：http：//localhost:5000/user/peishichao
传入url_for()的关键字参数不仅限于动态路由中的参数，函数能将任何额外参数添加到查询字符串中
url_for('index',page=2)的返回结果是/?page=2

'''

#app.route添加的method参数告诉Flask在URL映射中将视图注册为get和Post请求处理程序，如果没有指定methods参数
#就只把视图函数注册为Get请求处理程序
'''
点击浏览器刷新或看到一个莫名其妙的警告，要求在再次提交表单之前进行确认
之所以这样是因为刷新页面时浏览器会重新发送之前已经发送过的最后一个请求
如果这个请求时一个包含表单数据的Post请求的话，刷新页面会再次提交表单

可以使用重定向作为Post请求的响应，而不是常规相应
重定向是一种特殊的响应，响应的内容是URL
而不是包含HTML代码的字符串
这个页面的加载可能要多花几微秒的时间，因为要把第二个请求发给服务器
现在最后一个请求是Get请求，所以刷新命令能够像预期的那样正常使用。
这种技巧称为：Post - 重定向 - Get模式
'''


@app.route('/', methods=['GET', 'POST'])
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
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
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
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known = session.get('known',False), current_time=datetime.utcnow())
    #user_agent = request.headers.get('User-Agent')
    #return render_template('index.html', current_time=datetime.utcnow())
    #return '<h1>hello worlds!</h1>'

'''
Flask调用视图函数后，会将其返回作为相应的内容，
Http响应中一个很重要的部分是状态码，
@app.route('/')
def index():
    return '<h1>Bad request</h1>',400
'''


'''
如果不想返回由1,2,3个值组成的元组，flask视图函数还可以返回Response对象，
make_response()函数可接受多个参数，并返回一个Response，

from flask import make_response
@app.route('/')
def index():
    response = make_response('<h1> this document carries a cookie!</h1>')
    response.set_cookie('answer','43')
    return response
'''

'''
有一种名为重定向的特殊响应类型
重定向经常使用302状态码表示，指向的地址由location首部提供
重定向相应可以使用3个值形式的返回值生成，也可以在Response对象中设定

from flask import redirect
@app.route('/')
def index():
    return redirect('http://www.baidu.com')
    
'''


'''
特殊相应由abort函数生成，用于处理错误。

from flask import abort
@app.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return '<h1>hello,%s</h1>' %user.name
注意，abort不会把控制权还给调用它的函数，而是抛出异常把控制权交给web服务器
'''
@app.route('/user/<name>')
def  user(name):
    return render_template('user.html',name = name)
#客户端请求未知页面或路由时显示
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
#有未处理的异常时显示
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

if __name__ == '__main__':
    manager.run()

'''
以前的都是关系型数据库
不过最近几年文档数据库和键值对数据库成了流行的替代选择，这两种数据库合称 NoSQL数据库
SQL数据库擅长用高效且紧凑的形式存储结构化数据，这种数据库需要花费精力保证数据的一致性
NoSql数据库放宽了对这种一致性的要求，从而获得性能上的优势

数据库抽象层代码包供选择，例如SQLAlchemy和MonoEngine
可以使用抽象包直接处理高等级的Python对象

易用性：抽象层也称为对象关系映射(ORM)或对象文档映射（ODM）
性能：ORM和ODM对生产率的提升远远超过一丁点性能降低
可移植性：Sqlalchemy ORM支持很多关系型数据库
 Flask-SQLAlchemy
 
 
 MySQL mysql://username:password@hostname/database
'''