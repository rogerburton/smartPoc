from flask import Blueprint, render_template, request
from lxml import etree
import random
import string
import sys
import hashlib

# Import client BaseX
sys.path.append("/home/ubuntu/dev/basex_client")
import basex_conn

sign_bp = Blueprint("sign", __name__, template_folder="../templates")

# --- Helpers ---------------------------------------------------------------
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"

NS_DECL = (
    f"declare namespace cac=\"{CAC}\";\n"
    f"declare namespace cbc=\"{CBC}\";\n"
)


def _login_exists(login: str) -> bool:
    """Vérifie l'unicité du login dans BaseX en tenant compte des namespaces UBL."""
    xq = (
        NS_DECL
        + f'count(//Party[cac:AdditionalWebSite/cac:WebSiteAccess/cbc:Login="{login}"])'
    )
    return basex_conn.query("directory", xq) != "0"


def _id_exists(pid: str) -> bool:
    """Vérifie l'unicité de l'ID (PartyIdentification/ID)."""
    xq = NS_DECL + f'count(//Party[cac:PartyIdentification/cbc:ID="{pid}"])'
    return basex_conn.query("directory", xq) != "0"


def _new_party_id() -> str:
    while True:
        candidate = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        if not _id_exists(candidate):
            return candidate

# --- Routes ----------------------------------------------------------------
@sign_bp.route("/sign", methods=["GET", "POST"])
def sign():
    # GET → fragment si HTMX, sinon layout avec fragment
    if request.method == "GET":
        frag = render_template("sign_form.html")
        if request.headers.get("HX-Request") == "true":
            return frag
        return render_template("index.html", initial_title="Inscription", initial_content=frag)

    # POST
    family_name = request.form["family_name"].strip()
    first_name = request.form["first_name"].strip()
    birth_date = request.form["birth_date"].strip()
    tel = request.form["telephone"].strip()
    email = request.form["email"].strip()
    login = request.form["login"].strip()
    dwp = request.form["dwp"]
    uri = request.form["uri"].strip()

    # Unicité du login (namespace-aware)
    if _login_exists(login):
        msg = "<p style='color:red'>Login déjà utilisé</p>"
        if request.headers.get("HX-Request") == "true":
            return msg
        frag = render_template("sign_form.html") + msg
        return render_template("index.html", initial_title="Inscription", initial_content=frag)

    party_id = _new_party_id()

    # Construction XML UBL Party (root sans namespace; sous-éléments en CAC/CBC)
    nsmap = {"cac": CAC, "cbc": CBC}
    party = etree.Element("Party", nsmap=nsmap)

    pid = etree.SubElement(party, f"{{{CAC}}}PartyIdentification")
    etree.SubElement(pid, f"{{{CBC}}}ID").text = party_id

    person = etree.SubElement(party, f"{{{CAC}}}Person")
    etree.SubElement(person, f"{{{CBC}}}FamilyName").text = family_name
    etree.SubElement(person, f"{{{CBC}}}FirstName").text = first_name
    etree.SubElement(person, f"{{{CBC}}}BirthDate").text = birth_date

    contact = etree.SubElement(party, f"{{{CAC}}}Contact")
    etree.SubElement(contact, f"{{{CBC}}}Telephone").text = tel
    etree.SubElement(contact, f"{{{CBC}}}ElectronicMail").text = email

    aws = etree.SubElement(party, f"{{{CAC}}}AdditionalWebSite")
    access = etree.SubElement(aws, f"{{{CAC}}}WebSiteAccess")
    etree.SubElement(access, f"{{{CBC}}}URI").text = uri
    etree.SubElement(access, f"{{{CBC}}}Login").text = login
    hashed_dwp = hashlib.sha256(dwp.encode("utf-8")).hexdigest()
    etree.SubElement(access, f"{{{CBC}}}Password").text = hashed_dwp

    # Sauvegarde
    xml_str = etree.tostring(party, pretty_print=True, encoding="utf-8", xml_declaration=True)
    basex_conn.save("directory", party_id, xml_str.decode("utf-8"))

    success = f"<h2>Inscription réussie</h2><p>Party {party_id} créé avec login {login}</p>"
    if request.headers.get("HX-Request") == "true":
        return success
    return render_template("index.html", initial_title="Inscription réussie", initial_content=success)


@sign_bp.route("/check-login")
def check_login():
    login = request.args.get("login", "").strip()
    if len(login) < 5:
        return "<span style='color:red'>Minimum 5 caractères</span>"

    # Vérifie en DB (namespace-aware)
    if _login_exists(login):
        return "<span style='color:red'>Login indisponible</span>"
    return "<span style='color:green'>Login disponible</span>"
