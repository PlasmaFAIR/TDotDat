from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import login_required

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
        create_record(
            dict(
                title=form.title.data,
                software={"name": form.software.data},
                contributors=contributors,
            )
        )
        return redirect(url_for("deposit.success"))
    return render_template("deposit/create.html", form=form)


@blueprint.route("/success")
@login_required
def success():
    return render_template("deposit/success.html")
