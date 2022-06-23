from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import login_required
from invenio_files_rest.models import ObjectVersion, Bucket
import f90nml

from .forms import RecordForm
from .api import create_record


blueprint = Blueprint(
    "deposit",
    __name__,
    url_prefix="/deposit",
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/create", methods=("GET", "POST"))
@login_required
def create():
    form = RecordForm()
    if form.validate_on_submit():
        contributors = [dict(name=form.contributor_name.data)]

        bucket = None
        if form.input_file.data or form.output_file.data:
            bucket = Bucket.create()

        inputs = {}
        if form.input_file.data:
            input_file = request.files[form.input_file.name]
            in_file = ObjectVersion.create(
                bucket, input_file.filename, stream=input_file
            )
            in_file = dict(
                key=in_file.key,
                file_id=str(in_file.file_id),
                bucket=str(in_file.bucket_id),
            )

            input_file.seek(0)
            input_nml = f90nml.reads(input_file.read().decode("utf-8"))
            inputs["temperature"] = input_nml["species_parameters_1"]["temp"]
            inputs["temperature_gradient"] = input_nml["species_parameters_1"]["tprim"]
        else:
            in_file = None

        if form.output_file.data:
            output_file = request.files[form.output_file.name]
            out_file = ObjectVersion.create(
                bucket, output_file.filename, stream=output_file
            )
            out_file = dict(
                key=out_file.key,
                file_id=str(out_file.file_id),
                bucket=str(out_file.bucket_id),
            )
        else:
            out_file = None

        create_record(
            dict(
                title=form.title.data,
                software={"name": form.software.data},
                contributors=contributors,
                inputs=inputs,
                _bucket=str(bucket.id) if bucket else "",
                _input_files=[in_file],
                _output_files=[out_file],
            )
        )
        return redirect(url_for("deposit.success"))
    return render_template("deposit/create.html", form=form)


@blueprint.route("/success")
@login_required
def success():
    return render_template("deposit/success.html")
