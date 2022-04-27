import email
from functools import wraps
from os import abort
from flask import Flask, render_template, redirect, request, url_for, flash
import flask
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date, datetime
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import *
from flask_gravatar import Gravatar
import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)


gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLES



# creating another database class
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    
    #This will act like a List of BlogPost objects attached to each User. 
    #The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Coment", back_populates="author")
    
    
    
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    
    #Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    #Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
   
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Coment",back_populates="parent_post")
    
    
    

class Coment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.Text,nullable=False)
    
    author_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    
    post_id = db.Column(db.Integer,db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost",back_populates="comments")
   
   
class Reply(db.Model):
    __tablename__ = 'replyes'
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.Text,nullable=False) 
    
    
db.create_all()

def admin_user(f):
    @wraps(f)
    def wrapper_function(*args,**kwargs):
        if not current_user.id == 1:
            abort()
        return f(*args,**kwargs)
    return wrapper_function
        
        

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    year = datetime.datetime.now().year
    return render_template("index.html", all_posts=posts, current_user=current_user,year=year)


@app.route('/register', methods=['GET','POST'])
def register():
    # creting the form
    form = CreateUser()
    if form.validate_on_submit():
        user_name = form.name.data
        user_email = form.email.data
        user_password = generate_password_hash(form.password.data,"pbkdf2:sha256",8)
        new_user = User(email=user_email,name=user_name,password=user_password)
        current_user = User.query.filter_by(email=user_email).first()
        if current_user:
            flash("Already have an account please login")
            return redirect(url_for('login'))
        else:
            # adding to the database
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    year = datetime.datetime.now().year
    
    
    return render_template("register.html", form=form,year=year)


@app.route('/login',methods=['GET','POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash("The password is wrong")
        else:
            flash("There is no user ")
            return redirect(url_for('register'))
    year = datetime.datetime.now().year
    return render_template("login.html",form=form, current_user=current_user,year=year)


@app.route('/logout')
def logout():
    logout_user()
    year = datetime.datetime.now().year
    return redirect(url_for('login'))


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    comments = db.session.query(Coment).all()
    year = datetime.datetime.now().year
    return render_template("post.html", comments=comments, post=requested_post, current_user=current_user,year=year)


@app.route("/about")
@admin_user
def about():
    year = datetime.datetime.now().year
    return render_template("about.html",current_user=current_user,year=year)


@app.route("/contact")
def contact():
    year = datetime.datetime.now().year
    return render_template("contact.html",current_user=current_user,year=year)



@app.route("/new-post", methods=['GET','POST'])
@login_required
@admin_user
def add_new_post():
    form = CreatePostForm()
    new_post = BlogPost(
        title=form.title.data,
        subtitle=form.subtitle.data,
        body=form.body.data,
        img_url=form.img_url.data,
        author_id=current_user.id,
        date=(date.today().strftime("%B %d, %Y"))
    )     
    if form.validate_on_submit():
 
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    year = datetime.datetime.now().year
    return render_template("make-post.html", form=form,year=year)



@app.route("/edit-post/<int:post_id>",methods=['GET','POST'])
@admin_user
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    year = datetime.datetime.now().year
    return render_template("make-post.html", form=edit_form,current_user=current_user,year=year)


@app.route("/delete/<int:post_id>")
@admin_user
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    year = datetime.datetime.now().year
    return redirect(url_for('get_all_posts'))


@app.route('/comment/<int:id>', methods=['GET','POST'])
@login_required
def comment(id):
    post_to_comment = BlogPost.query.get(id)
    form = CommentForm()
    if form.validate_on_submit():
        text = form.text.data
        coment = Coment(
            author_id=current_user.id,
            post_id=post_to_comment.id,
            text=text
        )
        db.session.add(coment)
        db.session.commit()
        return redirect(url_for('show_post',post_id=post_to_comment.id))
    year = datetime.datetime.now().year
    return render_template('page.html',form=form,post=post_to_comment,year=year)


# this is for replying the post
@app.route('/reply/<int:post_id>',methods=['GET','POST'])
@admin_user
def reply_to_comment(post_id):
    year = datetime.datetime.now().year
    return render_template(year=year)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)
