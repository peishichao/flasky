import os
basedir = os.path.abspath(os.path.dirname(__file__))
'''
|-flasky
    |- app/
        |- templates/
        |- static/
        |- main/
            |- __init__.py
            |- errors.py
            |- forms.py
            |- views.py
        |- __init__.py
        |- email.py
        |- models.py
    |- migrations/
    |- tests/
        |-__init__.py
        |- test*.py
    |- venv/
    |- requirements.txt
    |- config.py
    |- manage.py
'''
class Config:
    # SECRET_KEY配置变量时通用秘钥，可以在多方扩展中使用
    # 为了增强安全性，秘钥不应该直接写入代码，而要保存在环境变量中
    SECRET_KEY = 'dfvdf@#$HKUIyibb'
    '''
    千万不要把账号秘钥直接写入脚本，特别是当你计划开源你自己的作品的时候，
    为了保护账号信息，你需要让脚本从环境中导入敏感信息

    环境变量中获取邮件服务器用户名和密码
    ubuntu$export MAIL_USERNAME = <Gmail username>
    windows$set MAIL_USERNAME = <Gmail username>
    '''
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # Email

    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'  # 邮件主题的前缀
    FLASKY_MAIL_SENDER = '15630965489@163.com'  # 发件人地址
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_APSSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URL = 'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URL = 'sqlite:///' + os.path.join(basedir,'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URL = 'sqlite:///' + os.path.join(basedir,'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
'''
基类中config中包含通用配置
子类分别定义专用的配置

配置基类可以定义init_app方法，其参数是程序实例
在这个方法中，可以执行当前环境的配置初始化

'''