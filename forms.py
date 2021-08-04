from wtforms import Form, TextField, PasswordField, validators
from wtforms.fields.html5 import EmailField

class RegistrationForm(Form):
    username = TextField("Username", [validators.Length(max=255)], render_kw={"class": "form-control"})
    email = EmailField('Email', [validators.Email()], render_kw={"class": "form-control"})
    password = PasswordField("Password", render_kw={"class": "form-control"})

class LoginForm(Form):
    username = TextField("Username", [validators.Length(max=255)], render_kw={"class": "form-control"})
    password = PasswordField("Password", render_kw={"class": "form-control"})