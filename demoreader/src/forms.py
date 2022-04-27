import email
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
    
    
# this is for the login form
class CreateUser(FlaskForm):
    email = EmailField("Enter your email id", validators=[DataRequired()])
    name = StringField("Enter your name ",validators=[DataRequired()])
    password = PasswordField("Enter your ids password",validators=[DataRequired()])
    submit = SubmitField("Sign Up")
    
    
# createing the login form
class Login(FlaskForm):
    email = EmailField("Enter the email id", validators=[DataRequired()])
    password = PasswordField("Enter the password", validators=[DataRequired()])
    submit = SubmitField("Log In")
    
    
class CommentForm(FlaskForm):
    text = CKEditorField("Enter your comment", validators=[DataRequired()])
    post = SubmitField("Submit")
