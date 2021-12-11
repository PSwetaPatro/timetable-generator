from flask import Blueprint, request, render_template
import os

from app.impl.model import FileDetail
from app.impl.scheduler import main

routes_bp = Blueprint("routes_bp", __name__)

filedetails = {}

files = tuple(os.walk("test_files/"))[-1][-1]
for file in files:
    with open(f"test_files/{file}") as f:
        filedetails[file] = main(file)


@routes_bp.route("/")
def index():
    return render_template("home.html", filedetails=filedetails)


# @routes_bp.route("/solve/<string:filename>")
# def solve_by_filename():
#     pass
