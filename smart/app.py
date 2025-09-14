from flask import Flask, render_template, session
from datetime import timedelta

# Blueprints
from routes.sign import sign_bp
from routes.auth import auth_bp

app = Flask(__name__, template_folder="templates")

# IMPORTANT : pas de url_prefix ici (Apache monte déjà l'app sur /smart)
app.register_blueprint(sign_bp, url_prefix="/smart")
app.register_blueprint(auth_bp, url_prefix="/smart")

# Clé secrète obligatoire pour utiliser les sessions
app.secret_key = "jenemesentisplusguidéparleshaleurs"

# Timeout d’inactivité : 5 minutes
app.permanent_session_lifetime = timedelta(minutes=5)


# La racine de l'app (côté Flask) devient "/"
@app.route("/")
@app.route("/smart/")
def index():
    return render_template(
        "index.html",
        initial_title="Home",
        initial_content="<h2>Bienvenue</h2><p>Choisissez une action dans le menu.</p>"
    )

if __name__ == "__main__":
    app.run(debug=True)
