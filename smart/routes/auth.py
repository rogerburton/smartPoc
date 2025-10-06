from flask import Blueprint, request, session
import sys
sys.path.append("/home/ubuntu/dev/basex_client")
import basex_conn
import hashlib

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    login = request.form["login"]
    password = request.form["password"]
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Vérifier dans BaseX
    result = basex_conn.query(
        "directory",
        f'count(//Party[AdditionalWebSite/WebSiteAccess/Login="{login}" '
        f'and AdditionalWebSite/WebSiteAccess/Password="{hashed_password}"])'
    )

    if result == "1":
        session.clear()  # tue toute session existante
        session.permanent = True  # active le timeout auto
        session["user"] = login
        return f"<p style='color:green'>Session ouverte pour {login}</p>"
    else:
        return "<p style='color:red'>Login ou mot de passe incorrect</p>"

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return "<p style='color:blue'>Session fermée</p>"
