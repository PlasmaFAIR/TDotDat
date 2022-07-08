from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from invenio_files_rest.models import ObjectVersion, Bucket
import pyrokinetics

from .forms import EquilibriumForm
from .api import create_equilibrium

blueprint = Blueprint(
    "equilibrium",
    __name__,
    url_prefix="/equilibrium",
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/search")
def search():
    return render_template("equilibrium/search.html")


@blueprint.route("/create", methods=("GET", "POST"))
@login_required
def create():
    form = EquilibriumForm()
    if not form.validate_on_submit():
        return render_template("equilibrium/create.html", form=form)

    bucket = Bucket.create()

    if form.input_file.data:
        input_file = request.files[form.input_file.name]
        in_file = ObjectVersion.create(bucket, input_file.filename, stream=input_file)

        # Note this relies on details of the file storage to get the filename
        print(in_file.file.storage().fileurl)
        pyro = pyrokinetics.Pyro(gk_file=in_file.file.storage().fileurl)

        data = {
            "elongation": pyro.local_geometry["kappa"],
            "q": pyro.local_geometry["q"],
            "B0": pyro.local_geometry["B0"],
            "_bucket": str(bucket.id),
            "_files": [
                dict(
                    key=f.key,
                    file_id=str(f.file_id),
                    bucket=str(bucket.id),
                    size=f.file.size,
                    checksum=f.file.checksum,
                    version_id=str(f.version_id),
                )
                for f in ObjectVersion.get_by_bucket(bucket.id)
            ],
        }
    else:
        data = {
            "elongation": form.elongation.data,
            "q": form.q.data,
            "B0": form.B0.data,
            "_bucket": str(bucket.id),
        }

    data["title"] = form.title.data

    data = {k: v for k, v in data.items() if v is not None}

    create_equilibrium(data)

    return redirect(url_for("equilibrium.success"))


@blueprint.route("/success")
@login_required
def success():
    return render_template("equilibrium/success.html")
