from flask import Blueprint
from ..models import Permission
'''
在单脚本中，程序实例会在与全局作用域中
路由可以直接使用app.route修饰符定义
但是现在程序在运行时创建，只有调用create_app()之后才能使用app.route修饰符
蓝本和程序类似，可以定义路由
蓝本可以在单个文件中定义，也可以使用更结构化的方式在包中的多个模块中创建
为了获得更大的灵活性，程序包中创建了一个子包，用于保存蓝本
通过实例化一个 Blueprint 类对象可以创建蓝本。这个构造函数有两个必须指定的参数：
蓝本的名字和蓝本所在的包或模块

'''

main = Blueprint('main',__name__)

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

from . import views, errors
#模块在末尾导入的原因是为了避免循环导入依赖
#因为在view和error中还要导入蓝本main