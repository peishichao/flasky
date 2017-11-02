from app import create_app
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import db
import os
'''

这个脚本先创建程序。如果已经定义了环境变量 FLASK_CONFIG ，则从中读取配置名；否则
使用默认配置。然后初始化 Flask-Script、Flask-Migrate 和为 Python shell 定义的上下文。
'''
app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)



'''
manager.command 修饰器让自定义命令变得简单。修饰函数名就是命令名，函数的文档字符
串会显示在帮助消息中。 test() 函数的定义体中调用了 unittest 包提供的测试运行函数。
(venv) $ python manage.py test
test_app_exists (test_basics.BasicsTestCase) ... ok
test_app_is_testing (test_basics.BasicsTestCase) ... ok
.----------------------------------------------------------------------
Ran 2 tests in 0.001s
OK
'''


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
