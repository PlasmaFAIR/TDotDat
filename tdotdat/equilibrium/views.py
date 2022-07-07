from flask import Blueprint


blueprint = Blueprint(
    "tdotdat_equilibrium",
    __name__,
    template_folder="templates",
    static_folder="static",
)
