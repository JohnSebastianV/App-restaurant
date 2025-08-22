from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class RegisterForm(FlaskForm):
    name = StringField("Nombre del restaurante", validators=[DataRequired(), Length(min=3)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    schedule = StringField("Horario")
    location = StringField("Ubicación")
    description = TextAreaField("Descripción")
    submit = SubmitField("Registrar")

class LoginForm(FlaskForm):
    name = StringField("Nombre del restaurante", validators=[DataRequired()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar Sesión")
