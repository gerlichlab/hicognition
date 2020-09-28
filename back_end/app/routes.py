"""Routes for HiCognition"""
import os
from collections import defaultdict
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import cooler
import pandas as pd
from ngs import HiCTools as HT
from hicognition import higlass_interface, io_helpers
from requests.exceptions import HTTPError
from app import app, db
from app.models import User, Dataset, Pileupregion, Pileup
from app.forms import (
    LoginForm,
    RegistrationForm,
    AddDatasetForm,
    SelectDatasetForm,
    DefinePileupRegionsForm,
    PileupForm
)


# user region mapping

DATASET_MAPPING = defaultdict(lambda: None)


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@app.route("/higlass", methods=["GET", "POST"])
@app.route("/api/higlass", methods=["GET", "POST"])
@login_required
def higlass():
    """Main app."""
    form = construct_dataset_select_form()
    form_region_select = DefinePileupRegionsForm()
    form_pileup = construct_pileup_form()
    # pileup define form has been submitted
    if form_region_select.submit_define.data and form_region_select.validate_on_submit():
        return handle_pileup_region_select(form_region_select)
    # region and cooler select form has been submitted
    if form.submit_select.data and form.validate_on_submit():
        # set current user attributes
        DATASET_MAPPING[current_user.id] = {"region": form.region.data, "cooler": form.cooler.data, "pileup_region": None}
        # redirect
        return redirect(url_for("higlass"))
    # pileup form has been submitted
    if form_pileup.submit_pileup.data and form_pileup.validate_on_submit():
        return handle_pileup_form(form_pileup)
    # render view using current user parameters
    current_user_dict = DATASET_MAPPING[current_user.id]
    if current_user_dict is not None:
        top_view, center_view = render_viewconfig(
            current_user_dict["region"], current_user_dict["cooler"], current_user_dict["pileup_region"]
        )
    else:
        top_view, center_view = [], []
    # get pileup location
    current_user_dict = DATASET_MAPPING[current_user.id]
    if (current_user_dict is None) or ("pileup" not in current_user_dict):
        pileup_file = "pileup_test.csv"
    else:
        pileup_entry = Pileup.query.get(current_user_dict["pileup"])
        pileup_file = pileup_entry.file_path
    pileup_path = "http://localhost:5000/static/" + pileup_file
    return render_template(
        "higlass.html",
        config=render_template(
            "config.json",
            server=app.config["HIGLASS_URL"],
            top=top_view,
            center=center_view,
        ),
        form=form,
        form_region_select=form_region_select,
        form_pileup=form_pileup,
        pileup_path=pileup_path
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for("higlass"))
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
            exit_code = higlass_interface.preprocess_dataset(
                "bedfile", app.config["CHROM_SIZES"], file_path, output_path
            )
            if exit_code != 0:
                print(f"Clodius failed")
                return redirect(url_for("higlass"))
            upload_file = output_path
        else:
            upload_file = file_path
        # add to higlass
        credentials = {
            "user": app.config["HIGLASS_USER"],
            "password": app.config["HIGLASS_PWD"],
        }
        try:
            result = higlass_interface.add_tileset(
                form.file_type.data,
                upload_file,
                app.config["HIGLASS_API"],
                credentials,
                form.name.data,
            )
        except HTTPError:
            print("Higlass upload failed!")
            return redirect(url_for("higlass"))
        # upload succeeded, add things to database
        uuid = result["uuid"]
        new_entry = Dataset(
            dataset_name=form.name.data,
            file_path=file_path,
            higlass_uuid=uuid,
            filetype=form.file_type.data,
        )
        # TODO: nice error handling for failed unique constraints
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for("higlass"))
    return render_template("add_dataset.html", form=form)


# Helper functions


def render_viewconfig(region_id, cooler_id, bedpe_id):
    """Takes region_id and cooler_id as well as bedpe_id (region_id and cooler_id are
    ids of the dataset table, bedpe_id is the id of the Pileupregion table)
    and renders a higlass viewconfig"""
    if (region_id is None) or (cooler_id is None):
        return [], []
    region_dataset = Dataset.query.get(region_id)
    cooler_dataset = Dataset.query.get(cooler_id)
    # construct top view
    top_view = render_template(
        "_topview.json",
        server=app.config["HIGLASS_URL"] + "/api/v1",
        uuid=region_dataset.higlass_uuid,
        name=region_dataset.dataset_name
    )
    # construct center view
    cooler_building_block = render_template(
        "_coolerview.json",
        server=app.config["HIGLASS_URL"] + "/api/v1",
        uuid=cooler_dataset.higlass_uuid,
        name=cooler_dataset.dataset_name
    )
    if bedpe_id is not None:
        bedpe_dataset = Pileupregion.query.get(bedpe_id)
        bedpe_building_block = render_template(
            "_bedpeview.json",
            server=app.config["HIGLASS_URL"] + "/api/v1",
            uuid=bedpe_dataset.higlass_uuid,
        )
        center_view = render_template(
            "_centerview.json",
            coolerview=cooler_building_block,
            bedpeview=bedpe_building_block,
        )
    else:
        center_view = render_template(
            "_centerview.json", coolerview=cooler_building_block
        )
    return top_view, center_view


def handle_pileup_region_select(form_pileup):
    """Handles event that pileup region
    select form has been submitted and validated."""
    # construct bedpe file from regions
    current_user_dict = DATASET_MAPPING[current_user.id]
    if current_user_dict is not None:
        current_region = current_user_dict["region"]
        input_region = Dataset.query.get(current_region)
        # check whether regions have been constructed with this windowsize before
        query_result = input_region.pileup_regions.filter_by(windowsize=form_pileup.windowsize.data).all()
        if len(query_result) != 0:
            # cache hit
            DATASET_MAPPING[current_user.id]["pileup_region"] = query_result[0].id
            return redirect(url_for("higlass"))
        input_file = input_region.file_path
        # sort file
        sorted_file_name = input_file.split(".")[0] + "_sorted.bed"
        io_helpers.sort_bed(input_file,
            sorted_file_name,
            app.config["CHROM_SIZES"]
        )
        target_file = sorted_file_name + f".{form_pileup.windowsize.data}" + ".bedpe"
        io_helpers.convert_bed_to_bedpe(
            sorted_file_name, target_file, form_pileup.windowsize.data
        )
        # preprocess with clodius
        clodius_output = target_file + ".bed2ddb"
        higlass_interface.preprocess_dataset(
            "bedpe", app.config["CHROM_SIZES"], target_file, clodius_output
        )
        # add to higlass
        credentials = {
            "user": app.config["HIGLASS_USER"],
            "password": app.config["HIGLASS_PWD"],
        }
        dataset_name = clodius_output.split("/")[-1]
        try:
            result = higlass_interface.add_tileset(
                "bedpe",
                clodius_output,
                app.config["HIGLASS_API"],
                credentials,
                dataset_name,
            )
        except HTTPError:
            print("Higlass upload failed!")
            return redirect(url_for("higlass"))
        # upload succeeded, add things to database
        uuid = result["uuid"]
        new_entry = Pileupregion(
            dataset_id=current_region,
            name=dataset_name,
            file_path=clodius_output,
            higlass_uuid=uuid,
            windowsize=form_pileup.windowsize.data,
        )
        db.session.add(new_entry)
        db.session.commit()
        # update current data dictionary
        DATASET_MAPPING[current_user.id]["pileup_region"] = new_entry.id
        return redirect(url_for("higlass"))


def handle_pileup_form(pileup_form):
    """Do ICCF pileup."""
    pileup_region_id = DATASET_MAPPING[current_user.id]["pileup_region"]
    if pileup_region_id is None:
        flash("No pileup regions defined!")
        return redirect(url_for("higlass"))
    # get pileup region dataset entry
    pileup_region = Pileupregion.query.get(pileup_region_id)
    # extract dataset location from related source datafile
    file_path = pileup_region.source_dataset.file_path
    # get windowsize, binsize and cooler path
    window_size = pileup_region.windowsize
    binsize = pileup_form.binsize.data
    cooler_id = DATASET_MAPPING[current_user.id]["cooler"]
    cooler_path = Dataset.query.get(cooler_id).file_path
    # check whether pileup has been performed before
    query_result = Pileup.query.filter_by(pileupregion_id=pileup_region_id, cooler_id=cooler_id, binsize=binsize).all()
    if len(query_result) != 0:
        # cache hit
        DATASET_MAPPING[current_user.id]["pileup"] = query_result[0].id
        return redirect(url_for("higlass"))
    # load bedfile
    regions = pd.read_csv(file_path, sep="\t", header=None).rename(columns={0: "chrom", 1: "start", 2: "end"})
    regions.loc[:, "pos"] = (regions["start"] + regions["end"])//2
    # do pileup
    arms = HT.get_arms_hg19()
    cooler_file = cooler.Cooler(cooler_path + f"::/resolutions/{binsize}")
    pileup_windows = HT.assign_regions(window_size, int(binsize), regions["chrom"], regions["pos"], arms).dropna()
    pileup_array = HT.do_pileup_iccf(cooler_file, pileup_windows, proc=2)
    # prepare dataframe for d3
    output_frame = pd.DataFrame(pileup_array)
    output_molten = output_frame.stack().reset_index().rename(columns={"level_0": "variable", "level_1": "group", 0: "value"})
    # scale output so that colormap can be adjusted in integer steps
    output_molten.loc[:, "value"] = output_molten["value"] * 10000
    # stitch together filepath
    basedir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(basedir, "static")
    file_name = file_path.split("/")[-1] + f".{window_size}" + f".{binsize}.csv"
    output_molten.to_csv(os.path.join(static_dir, file_name), index=False)
    # add this to database
    new_entry = Pileup(binsize=int(binsize), name=file_name, file_path=file_name, pileupregion_id=pileup_region_id,
                       cooler_id=cooler_id)
    db.session.add(new_entry)
    db.session.commit()
    # add this to data mapping
    DATASET_MAPPING[current_user.id]["pileup"] = new_entry.id
    return redirect(url_for("higlass"))



def construct_dataset_select_form():
    """constructs select dataset form"""
    # Construct select dataset form
    form = SelectDatasetForm()
    # select region files for region choices
    bed_files = Dataset.query.filter(Dataset.filetype == "bedfile").all()
    bed_display = [(i.id, i.dataset_name) for i in bed_files]
    form.region.choices = bed_display
    # select cooler files for cooler choices
    cooler_files = Dataset.query.filter(Dataset.filetype == "cooler").all()
    cooler_display = [(i.id, i.dataset_name) for i in cooler_files]
    form.cooler.choices = cooler_display
    return form


def construct_pileup_form():
    """Makes the region select form"""
    form_pileup = PileupForm()
    if DATASET_MAPPING[current_user.id] is None:
        choices = []
    else:
        cooler_id = DATASET_MAPPING[current_user.id]["cooler"]
        # get filepath for cooler
        cooler_file = Dataset.query.get(cooler_id)
        path = cooler_file.file_path
        multires_paths = cooler.fileops.list_coolers(path)
        choices = [
            (i.split("/resolutions/")[1], i.split("/resolutions/")[1])
            for i in multires_paths
        ]
    form_pileup.binsize.choices = choices
    return form_pileup