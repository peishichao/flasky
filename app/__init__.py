from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

'''
在单个文件中开发程序很重要，但是却有很大的缺点
因为程序在全局作用中创建，无法动态修改配置
运行脚本时，程序实例已经创建，无法再次修改

对于单元测试为了提高测试覆盖度，必须在不同的配置环境中运行程序
这种问题的解决办法是延迟创建程序实例
把创建过程移植到可显式调用的工厂函数中
这种方法不仅可以给脚本留出配置程序的时间
还可以创建多个程序实例
这些实例有时候在测试中非常有用
程序的工厂函数在app包的构造文件中定义

构造文件导入大多数正在使用的Flask扩展
由于尚未初始化所需的程序实例
所以没有初始化扩展
创建扩展类时没有向构造函数传入参数
create_app()函数就是程序的工厂函数接受一个参数是程序使用的配置名
配置类在config.py文件中定义
其中保存的配置可以使用flask app.config配置对象提供的from_object（）方法直接导入程序
置于配置对象，则可以通过名字从config字典中选择
程序创建并配置好之后，就能初始化扩展

'''
'''
LoginManager 对象的 session_protection 属性可以设为 None 、 'basic' 或 'strong' ，以提
供不同的安全等级防止用户会话遭篡改。设为 'strong' 时，Flask-Login 会记录客户端 IP
地址和浏览器的用户代理信息，如果发现异动就登出用户。 login_view 属性设置登录页面
的端点。回忆一下，登录路由在蓝本中定义，因此要在前面加上蓝本的名字。
'''
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    login_manager.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')
    #附加路由和自定义的错误页面
    return app