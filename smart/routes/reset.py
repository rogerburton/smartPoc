from flask import Blueprint, render_template, request
import sys, traceback

# Import paresseux de basex_conn pour éviter plantage si indisponible
sys.path.append("/home/ubuntu/dev/basex_client")
import basex_conn

reset_bp = Blueprint("reset", __name__, template_folder="../templates")

@reset_bp.route("/reset", methods=["GET", "POST"])
def reset():
    try:
        if request.method == "POST":
            # Effacement complet de la DB directory
            basex_conn.delete_all("directory")
            return "<h2>Base réinitialisée</h2><p>La base directory est maintenant vide.</p>"

        # Si GET → afficher le formulaire avec confirmation
        return render_template("reset_confirm.html")

    except Exception as e:
        err = traceback.format_exc()
        return f"<pre style='color:red'>{err}</pre>"
