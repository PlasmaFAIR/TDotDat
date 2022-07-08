from flask import Blueprint, render_template


blueprint = Blueprint(
    "tdotdat_equilibrium",
    __name__,
    url_prefix="/equilibrium",
    template_folder="templates",
    static_folder="static",
)


@blueprint.route("/search")
def search():
    return render_template("equilibrium/search.html")
