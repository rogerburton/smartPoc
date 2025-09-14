from flask import Blueprint, render_template, request
from lxml import etree
import random, string
import sys
sys.path.append("/home/ubuntu/dev/basex_client")  # chemin vers ton module sécurisé
import basex_conn
import hashlib

sign_bp = Blueprint("sign", __name__, template_folder="../templates")

def generate_id():
    """
    Génère un ID unique de 6 caractères (lettres/chiffres)
    et vérifie qu'il n'existe pas déjà dans la DB BaseX 'directory'.
    """
    while True:
        candidate = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        
        # Vérifie si l'ID existe déjà comme Party/PartyIdentification/ID
        exists = basex_conn.query(
            "directory",
            f'count(//Party[PartyIdentification/ID="{candidate}"])'
        )
        
        if exists == "0":
            return candidate

@sign_bp.route("/sign", methods=["GET", "POST"])
def sign():
    if request.method == "POST":
        family_name = request.form["family_name"]
        first_name = request.form["first_name"]
        birth_date = request.form["birth_date"]
        tel = request.form["telephone"]
        email = request.form["email"]
        login = request.form["login"]
        dwp = request.form["dwp"]
        uri = request.form["uri"]

        # Vérifier unicité du login
        exists = basex_conn.query(
            "directory",
            f'count(//Party[AdditionalWebSite/WebSiteAccess/Login="{login}"])'
        )
        if exists != "0":
            return "<p style='color:red'>Login déjà utilisé</p>"

        party_id = generate_id()

        # Construction XML UBL Party
        ns_cbc = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        ns_cac = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        nsmap = {"cbc": ns_cbc, "cac": ns_cac}
        party = etree.Element("Party", nsmap=nsmap)

        pid = etree.SubElement(party, f"{{{ns_cac}}}PartyIdentification")
        etree.SubElement(pid, f"{{{ns_cbc}}}ID").text = party_id

        person = etree.SubElement(party, f"{{{ns_cac}}}Person")
        etree.SubElement(person, f"{{{ns_cbc}}}FamilyName").text = family_name
        etree.SubElement(person, f"{{{ns_cbc}}}FirstName").text = first_name
        etree.SubElement(person, f"{{{ns_cbc}}}BirthDate").text = birth_date

        contact = etree.SubElement(party, f"{{{ns_cac}}}Contact")
        etree.SubElement(contact, f"{{{ns_cbc}}}Telephone").text = tel
        etree.SubElement(contact, f"{{{ns_cbc}}}ElectronicMail").text = email

        aws = etree.SubElement(party, f"{{{ns_cac}}}AdditionalWebSite")
        access = etree.SubElement(aws, f"{{{ns_cac}}}WebSiteAccess")
        etree.SubElement(access, f"{{{ns_cbc}}}URI").text = uri
        etree.SubElement(access, f"{{{ns_cbc}}}Login").text = login
        hashed_dwp = hashlib.sha256(dwp.encode("utf-8")).hexdigest()
        etree.SubElement(access, f"{{{ns_cbc}}}Password").text = hashed_dwp

        # Sauvegarde dans BaseX
        xml_str = etree.tostring(party, pretty_print=True, encoding="utf-8", xml_declaration=True)
        basex_conn.save("directory", party_id, xml_str.decode("utf-8"))
        return f"<h2>Inscription réussie</h2><p>Party {party_id} créé avec login {login}</p>"

    # si c'est un appel htmx → juste le fragment
    if request.headers.get("HX-Request") == "true":
        return render_template("sign_form.html")

    # sinon (URL directe dans le navigateur) → layout complet
    return render_template(
        "index.html",
        initial_title="Inscription",
        initial_content=render_template("sign_form.html")
    )

@sign_bp.route("/check-login")
def check_login():
    login = request.args.get("login", "").strip()

    if len(login) < 5:
        return "<span style='color:red'>Minimum 5 caractères</span>"

    # Vérifie en DB si login existe
    result = basex_conn.query(
        "directory",
        f'count(//Party[AdditionalWebSite/WebSiteAccess/Login="{login}"])'
    )

    if result != "0":
        return "<span style='color:red'>Login indisponible</span>"
    else:
        return "<span style='color:green'>Login disponible</span>"
