from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import login_required
from invenio_files_rest.models import ObjectVersion, Bucket
import pyrokinetics

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

        bucket = Bucket.create()

        inputs = {}
        if form.input_file.data:
            input_file = request.files[form.input_file.name]
            in_file = ObjectVersion.create(
                bucket, input_file.filename, stream=input_file
            )

            # Note this relies on details of the file storage to get the filename
            print(in_file.file.storage().fileurl)
            pyro = pyrokinetics.Pyro(gk_file=in_file.file.storage().fileurl)

            inputs["temperature"] = pyro.local_species["electron"].temp
            inputs["temperature_gradient"] = pyro.local_species["electron"].a_lt
            inputs["files"] = [in_file.key]

            software_name = pyro.gk_code
        else:
            in_file = None
            software_name = form.software.data

        outputs = {}
        if form.output_file.data:
            output_file = request.files[form.output_file.name]
            out_file = ObjectVersion.create(
                bucket, output_file.filename, stream=output_file
            )
            outputs["files"] = [out_file.key]
        else:
            out_file = None

            out_file = dict(
                key=out_file.key,
                file_id=str(out_file.file_id),
                bucket=str(out_file.bucket_id),
            )

        files = [
            dict(
                key=f.key,
                file_id=str(f.file_id),
                bucket=str(bucket.id),
                size=f.file.size,
                checksum=f.file.checksum,
                version_id=str(f.version_id),
            )
            for f in ObjectVersion.get_by_bucket(bucket.id)
        ]

        create_record(
            dict(
                title=form.title.data,
                software={"name": software_name},
                contributors=contributors,
                inputs=inputs,
                outputs=outputs,
                _bucket=str(bucket.id),
                _files=files,
            )
        )
        return redirect(url_for("deposit.success"))
    return render_template("deposit/create.html", form=form)


@blueprint.route("/success")
@login_required
def success():
    return render_template("deposit/success.html")
