from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class TaskForm(FlaskForm):
    task = StringField("Новая задача", validators=[
        InputRequired(message="Введите текст задачи"),
        Length(max=200, message="Задача не должна превышать 200 символов")
    ])
    submit = SubmitField("Добавить")


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
