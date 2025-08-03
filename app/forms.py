from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class RegisterForm(FlaskForm):
    username = StringField("Логин", validators=[
        DataRequired(message="Введите логин"),
        Length(min=3, max=50)
    ])
    password = PasswordField("Пароль", validators=[
        DataRequired(message="Введите пароль"),
        Length(min=6)
    ])
    submit = SubmitField("Создать аккаунт")

class LoginForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")
