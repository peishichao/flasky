from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
import hashlib

'''
Model
'''
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    '''
    (venv) $ python manage.py shell
    >>> User.generate_fake(100)
    >>> Post.generate_fake(100)
    '''

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint

        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                 timestamp=forgery_py.date.date(True),
                 author=u)
        db.session.add(p)
        db.session.commit()


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' %self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
        if role is None:
            role = Role(name=r)
        role.permissions = roles[r][0]
        role.default = roles[r][1]
        db.session.add(role)
        db.session.commit()

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

'''

两个时间戳的默认值都是当前时间。注意， datetime.utcnow 后面没有 () ，因为 db.Column()
的 default 参数可以接受函数作为默认值，所以每次需要生成默认值时， db.Column() 都会
调用指定的函数。
'''
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index = True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys = [Follow.followers_id],
                               backref = db.backref('follower',lazy='joined'),
                               lazy = 'dynamic',
                               cascade = 'all,delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys = [Follow.followed_id],
                                backref = db.backref('followed',lazy='joined'),
                                lazy = 'dynamic',
                                cascade = 'all,delete-orphan')


    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id == Post.author_id)\
                .filter(Follow.follower_id == self.id)
    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower = self,followed = user)
            db.session.add(f)
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id = user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self,user):
        return self.followed.filter_by(followed_id = user.id).first() is not None
    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def ping(self):
        self.last_seen = datetime.utcnow()

        db.session.add(self)
    def __int__(self,**kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self,permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
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
    generate_confirmation_token() 方法生成一个令牌，有效期默认为一小时。 
    confirm() 方法检验令牌，如果检验通过，则把新添加的 confirmed 属性设为 True 。
    除了检验令牌， confirm() 方法还检查令牌中的 id 是否和存储在 current_user 中的已登录
    用户匹配。如此一来，即使恶意用户知道如何生成签名令牌，也无法确认别人的账户。
    '''
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)

        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'

        else:
            url = 'http://www.gravatar.com/avatar'
            hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     confirmed = True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me = forgery_py.lorem_ipsum.sentence(),
                     member_since = forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

'''
itsdangerous 提供了多种生成令牌的方法。其中， TimedJSONWebSignatureSerializer 类生成
具有过期时间的 JSON Web 签名（JSON Web Signatures，JWS）。这个类的构造函数接收
的参数是一个密钥，在 Flask 程序中可使用 SECRET_KEY 设置。
dumps() 方法为指定的数据生成一个加密签名，然后再对数据和签名进行序列化，生成令
牌字符串。 expires_in 参数设置令牌的过期时间，单位为秒。
为了解码令牌，序列化对象提供了 loads() 方法，其唯一的参数是令牌字符串。这个方法
会检验签名和过期时间，如果通过，返回原始数据。如果提供给 loads() 方法的令牌不正
确或过期了，则抛出异常。
'''
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser

'''
registrations = db.Talbe('registrations',
                db.Column('student_id',db.Integer,db.ForeignKey('stundents.id')),
                db.Column('class_id',db.Integer,db.ForeignKey('classes.id')))
class Student(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    classes = db.relationship('Class',secondary = registrations,
                                backref = db.backref('students',lazy='dynamic'),
                                lazy = 'dynamic')
class Class(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String)
    stundets = db.relationship('Student',secondary = registrations,
                                backref = db.backref('classes',lazy = 'dynamic'),
                                lazy = 'dynamic')

多对多关系仍然使用定义一对多关系的db.relationship方法进行定义，但在多对多的关系中
必须把secondary参数设为关联表。多对多关系可以在任何一个类中定义，backref参数会处理好关系的另一侧
关联表就是一个简单的表，而不是模型

多对多的关系可以实现用户之间的关注，但是还有一个问题，就是关联表连接的是两个明确的实体
但是表示用户关注其他用户时候，只有用户一个实体
                                
'''