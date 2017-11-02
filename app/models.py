from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
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
'''
最后，Flask-Login 要求程序实现一个回调函数，使用指定的标识符加载用户。
加载用户的回调函数接收以 Unicode 字符串形式表示的用户标识符。
如果能找到用户，这个函数必须返回用户对象；否则应该返回 None 。
'''


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index = True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise  AttributeError('password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    def __repr__(self):
        return '<User %r>' %self.username
'''

'''