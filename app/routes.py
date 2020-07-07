"""Routes for HiCognition"""
import os
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User
from app.forms import LoginForm, RegistrationForm, AddDatasetForm


@app.route("/")
@app.route("/index")
@app.route("/higlass")
@login_required
def higlass():
    """Main app."""
    return render_template(
        "higlass.html",
        config=render_template("config.json", server=app.config["HIGLASS_URL"]),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("higlass")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    """Logout route."""
    logout_user()
    return redirect(url_for("higlass"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register route."""
    if current_user.is_authenticated:
        return redirect(url_for("higlass"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/addDataset", methods=["Get", "Post"])
@login_required
def add_dataset():
    """Add dataset"""
    form = AddDatasetForm()
    if form.validate_on_submit():
        print(form.name)
        print(form.filePath)
        f = form.filePath.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config["UPLOAD_DIR"], filename))
        flash("Added dataset successfully!")
        return redirect(url_for("higlass"))
    return render_template("add_dataset.html", form=form)
