from flask import Blueprint, request, render_template

routes_bp = Blueprint("routes_bp", __name__)


@routes_bp.route("/")
def index():
    return render_template("home.html")
