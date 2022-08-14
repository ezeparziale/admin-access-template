from flask import Blueprint, render_template

about_bp = Blueprint(
    "about",
    __name__,
    url_prefix="/about",
    template_folder="templates",
    static_folder="static",
)


@about_bp.route("/")
def about_view():
    return render_template("about/about.html")
