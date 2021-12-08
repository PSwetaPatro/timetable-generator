from flask import Blueprint, request, render_template
import os

routes_bp = Blueprint("routes_bp", __name__)


@routes_bp.route("/")
def index():
    files = tuple(os.walk("test_files/"))[-1][-1]
    file_contents = {}
    for file in files:
        with open(f"test_files/{file}") as f:
            file_contents[file] = f.read()
    return render_template(
        "home.html",
        file_contents=file_contents,
    )
