from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email

'''
电子邮件字段用到了 WTForms 提供的 Length() 和 Email() 验证函数。 
PasswordField 类表示属性为 type="password" 的 <input> 元素。 
BooleanField 类表示复选框。
'''


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')