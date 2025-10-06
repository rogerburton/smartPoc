from flask import Blueprint, render_template, request
import sys, traceback

# Import paresseux de basex_conn pour éviter plantage si indisponible
sys.path.append("/home/ubuntu/dev/basex_client")
import basex_conn

reset_bp = Blueprint("reset", __name__, template_folder="../templates")

@reset_bp.route("/reset", methods=["GET", "POST"])
@reset_bp.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        basex_conn.drop_and_recreate("directory")
        return "<h2>Base 'directory' supprimée et recréée</h2>"

    return render_template("reset_confirm.html")