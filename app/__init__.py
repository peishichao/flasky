from flask import Flask, render_template
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from app import config

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

'''


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    #附加路由和自定义的错误页面
    return app