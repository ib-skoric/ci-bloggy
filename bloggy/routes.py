from flask import (
    render_template, redirect,
    request, session, url_for)
from bloggy import app
from bloggy.forms import RegisterForm, LoginForm
from bloggy.utilities import all_posts, featured_posts

'''Define index route'''
@app.route('/')
def index():
    return render_template('index.html', all_posts=all_posts, featured_posts=featured_posts)

'''Define login route'''
@app.route('/login', methods=("GET", "POST"))
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

'''Define register route'''
@app.route('/register', methods=("GET", "POST"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect(url_for('register.html'), form=form)
    return render_template('register.html', form=form)
