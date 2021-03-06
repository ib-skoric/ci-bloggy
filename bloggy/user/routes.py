from flask import (
    Blueprint, render_template, redirect,
    request, session, url_for, flash)
from bloggy import app, mongo, bcrypt, ObjectId
from bloggy.forms import RegisterForm, LoginForm, EditProfileForm
from slugify import slugify
from flask_paginate import Pagination, get_page_parameter
from bloggy.utilities import (check_username,
                              get_user_id_from_username, get_users_posts,
                              get_blog_from_user_id, get_user_from_username)


user = Blueprint("user", __name__)


@user.route('/login', methods=("GET", "POST"))
def login():
    '''Define login route'''
    # Check if user is in session, if true redirect them to user page
    if "user" in session:
        return redirect(url_for('user.user_page'))
    # Define WTForms form
    form = LoginForm()
    # Check form validation refer to forms.py file for validators
    if form.validate_on_submit():
        # Check username in database
        user = check_username(form.username.data)
        # Get users password
        user_password = user["password"]
        # Get input field password
        input_password = form.password.data
        # Check if credentials match
        if bcrypt.check_password_hash(user_password, input_password):
            session["user"] = form.username.data.lower()
            flash("You've been logged in successfully")
            return redirect(url_for('user.user_page'))
        # Else if they don't:
        else:
            flash("Details incorrect")
    return render_template('login.html', form=form)


@user.route('/logout')
def logout():
    '''Define log out route'''
    # Pop the user out of the session
    session.pop("user")
    flash("You have been logged out successfully")
    return redirect(url_for('main.index'))


@user.route('/register', methods=("GET", "POST"))
def register():
    '''Define register route'''
    # Define WTForms form
    form = RegisterForm()
    # Define default profile image if user doesn't supply one
    profile_img_url = 'https://cdn.pixabay.com/photo/2017/03/25/17/55/color-2174045_960_720.png'
    if form.validate_on_submit():
        # Check if form field is empty and
        # if it is give it default profile image
        if form.profile_img_url.data == '':
                profile_img_url = profile_img_url
        # Else if not get actual field value
        else:
                profile_img_url = form.profile_img_url.data
        # Hash the password from the input field first
        hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
        # Define register_user dictionary
        register_user = {
            "username": form.username.data,
            "password": hashed_password,
            "email": form.email.data,
            "profile_img_url": profile_img_url
            }
        # Get the inserted user's ID
        registered_usr_id = mongo.db.users.insert_one(register_user)
        # Define register blog dictionary
        register_blog = {
            "owner_id": ObjectId(registered_usr_id.inserted_id),
            "title": form.blog_title.data,
            "title-slug": slugify(form.blog_title.data),
            "description": form.blog_description.data
        }
        # Insert blog details into the database
        mongo.db.blogs.insert_one(register_blog)
        # All goes well display flash m essage & return user to login form
        flash(
            "You have been sucessfully registered, you can now log in below")
        return redirect(url_for('user.login'))
    return render_template('register.html', form=form)


@user.route('/user', methods=("GET", "POST"))
def user_page():
    '''Define user page route'''
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 6
    # Get current user
    current_user = session.get("user")
    # Get current user, ID & blog
    user = get_user_from_username(current_user)
    current_user_id = user["_id"]
    current_blog = get_blog_from_user_id(current_user_id)
    # Check if user is admin if it is, display all posts
    if current_user == 'admin':
        users_posts = mongo.db.posts.find().skip(
            (page-1) * per_page).limit(per_page)
    if current_user != 'admin':
        # Get current user's posts
        users_posts = get_users_posts(
            current_user_id).skip((page-1) * per_page).limit(per_page)
    # Handle sorting if value is X sort by Y
    if request.form.get('sort') == "1":
        users_posts = users_posts.sort("last_updated", -1)
    if request.form.get('sort') == "2":
        users_posts = users_posts.sort("last_updated", 1)
    if request.form.get('sort') == "3":
        users_posts = users_posts.sort("title", 1)
    if request.form.get('sort') == "4":
        users_posts = users_posts.sort("title", -1)
    if request.form.get('sort') == "5":
        users_posts = users_posts.sort("views", -1)
    if request.form.get('sort') is None:
        users_posts = users_posts
    sorting_value = request.form.get('sort')
    pagination = Pagination(
        page=page, per_page=per_page, total=users_posts.count(),
        record_name='posts')
    return render_template(
        'user.html', users_posts=users_posts,
        pagination=pagination, blog=current_blog,
        user=user, sorting_value=sorting_value)


@user.route('/user/edit', methods=("GET", "POST"))
def edit_user():
    '''Define edit user page route'''
    # Define WTForm
    form = EditProfileForm()
    # Get current user
    current_user = session.get("user")
    # Check if user is logged in
    if current_user is not None:
        user = get_user_from_username(current_user)
        # Get current password
        current_user_pasword = user["password"]
        current_profile_pic = user["profile_img_url"]
        # Get current blog description
        blog = get_blog_from_user_id(user["_id"])
        current_blog_description = blog["description"]
        # Get input existing password
        password_to_check = form.existing_password.data
        if form.validate_on_submit():
            # Check that existing password is not empty
            if form.existing_password.data != '':
                    if form.new_password.data and form.confirm_new_password.data != '':
                        # Check that new password and
                        # confirm new password match
                        if form.new_password.data == form.confirm_new_password.data:
                            # check that existing password matches the db entry
                            if bcrypt.check_password_hash(
                                    user["password"], password_to_check):
                                new_password = bcrypt.generate_password_hash(
                                    form.new_password.data).decode('utf-8')
                                update_password = {"$set": {"password": new_password}}
                                mongo.db.users.update(user, update_password)
                                flash("Profile successfully updated")
                                return redirect(url_for('user.user_page'))
                            else:
                                flash("Current password is not correct")
                                return redirect(url_for('user.edit_user'))
                        else:
                            flash("Passwords must match")
                            return redirect(url_for('user.edit_user'))
                    else:
                        flash("You entered your existing password"
                              "but not the new password"
                              "Please check your fields and try again")
                        return redirect(url_for('user.edit_user'))
            if form.profile_pic.data != '':
                new_profile_pic = form.profile_pic.data
                update_profile_pic = {"$set": {"profile_img_url": new_profile_pic}}
                mongo.db.users.update(user, update_profile_pic)
                flash("Profile successfully updated")
                return redirect(url_for('user.user_page'))
            flash("Profile image URL field can't be empty")
            return redirect(url_for('user.edit_user'))
        return render_template('edit_user.html', user=user,
                               form=form, current_user=current_user,
                               current_profile_pic=current_profile_pic)
    flash("You must be logged in to access this page")
    return redirect(url_for('main.index'))
