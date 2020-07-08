"""Routes for HiCognition"""
import os
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from hicognition import higlass_interface
from requests.exceptions import HTTPError
from app import app, db
from app.models import User, Dataset
from app.forms import LoginForm, RegistrationForm, AddDatasetForm, SelectDatasetForm


# map for view update

DATATYPES = {"bedfile": "bedlike",
             "cooler": "heatmap"}


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@app.route("/higlass", methods=["GET", "POST"])
@login_required
def higlass():
    """Main app."""
    form = SelectDatasetForm()
    # select region files for region choices
    bed_files = Dataset.query.filter(Dataset.filetype == "bedfile").all()
    bed_display = [(i.id, i.dataset_name) for i in bed_files]
    form.region.choices = bed_display
    # select cooler files for cooler choices
    cooler_files = Dataset.query.filter(Dataset.filetype == "cooler").all()
    cooler_display = [(i.id, i.dataset_name) for i in cooler_files]
    form.cooler.choices = cooler_display
    if form.validate_on_submit():
        # construct new view
        print(form.region.data)
        print(form.cooler.data)
        region_dataset = Dataset.query.get(form.region.data)
        cooler_dataset = Dataset.query.get(form.cooler.data)
        # construct top view
        top_view = render_template("_topview.json", server=app.config["HIGLASS_URL"] + "/api/v1", 
                            uuid=region_dataset.higlass_uuid,
                            filetype=DATATYPES[region_dataset.filetype],
                            name=region_dataset.dataset_name)
        # construct center view
        center_view = render_template("_centerview.json", server=app.config["HIGLASS_URL"] + "/api/v1", 
                    uuid=cooler_dataset.higlass_uuid,
                    filetype=DATATYPES[cooler_dataset.filetype],
                    name=cooler_dataset.dataset_name)
        return render_template("higlass.html",
                                config=render_template("config.json",
                                server=app.config["HIGLASS_URL"], top=top_view, center=center_view),
                                form=form)
    # construct default topview
    top_view = render_template("_topview.json", server=app.config["HIGLASS_URL"] + "/api/v1", 
                               uuid="Txg3Ri04TLeyWKeZT_lQ4Q",
                               filetype="bedlike",
                               name="test")
    return render_template(
        "higlass.html",
        config=render_template("config.json", server=app.config["HIGLASS_URL"], top=[], center=[]),
        form=form)


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
        print(form.name.data)
        print(form.filePath.data)
        # save locally
        f = form.filePath.data
        filename = secure_filename(f.filename)
        file_path = os.path.join(app.config["UPLOAD_DIR"], filename)
        f.save(file_path)
        # preprocess with clodius if file is bedfile
        if form.file_type.data == "bedfile":
            output_path = os.path.join(app.config["UPLOAD_DIR"], filename + ".beddb")
            exit_code = higlass_interface.preprocess_dataset("bedfile",
                                                 app.config["CHROM_SIZES"],
                                                 file_path,
                                                 output_path)
            if exit_code != 0:
                print(f"Clodius failed")
                return redirect(url_for("higlass"))
            upload_file = output_path
        else:
            upload_file = file_path
        # add to higlass
        credentials = {"user": app.config["HIGLASS_USER"],
                       "password": app.config["HIGLASS_PWD"]}
        try:
            result = higlass_interface.add_tileset(form.file_type.data,
                                                upload_file,
                                                app.config["HIGLASS_API"],
                                                credentials,
                                                form.name.data)
        except HTTPError:
            print("Higlass upload failed!")
            return redirect(url_for("higlass"))
        # upload succeeded, add things to database
        uuid = result['uuid']
        new_entry = Dataset(dataset_name=form.name.data,
                            file_path=file_path,
                            higlass_uuid=uuid,
                            filetype=form.file_type.data)
        # TODO: nice error handling for failed unique constraints
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for("higlass"))
    return render_template("add_dataset.html", form=form)
