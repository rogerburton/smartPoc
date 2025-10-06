# /var/www/html/smart/routes/doc.py
from __future__ import annotations
import os, base64
from typing import List
from flask import Blueprint, request, jsonify, render_template, current_app
import requests
from lxml import etree

doc_bp = Blueprint("doc", __name__)

# --- Config BaseX via env (avec valeurs par défaut)
BASEX_URL = os.environ.get("BASEX_URL", "http://127.0.0.1:8080/rest")
BASEX_DB  = os.environ.get("BASEX_DB",  "DOCDB")
BASEX_RES = os.environ.get("BASEX_RES", "posts.xml")
BASEX_USER = os.environ.get("BASEX_USER", "admin")
BASEX_PASS = os.environ.get("BASEX_PASS", "admin")

def _rest_url() -> str:
    return f"{BASEX_URL.rstrip('/')}/{BASEX_DB}/{BASEX_RES}"

def _auth_header() -> dict:
    token = base64.b64encode(f"{BASEX_USER}:{BASEX_PASS}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def fetch_posts() -> List[str]:
    r = requests.get(_rest_url(), headers=_auth_header())
    if r.status_code == 404:
        return []
    r.raise_for_status()
    try:
        root = etree.fromstring(r.content)
    except etree.XMLSyntaxError:
        return []
    return [(p.text or "") for p in root.findall("post")]

def save_posts(posts: List[str]) -> None:
    root = etree.Element("posts")
    for i, content in enumerate(posts, start=1):
        el = etree.SubElement(root, "post")
        el.set("n", str(i))
        el.text = etree.CDATA(content)
    xml_bytes = etree.tostring(root, xml_declaration=True, encoding="utf-8", pretty_print=True)
    r = requests.put(_rest_url(), headers={**_auth_header(), "Content-Type": "application/xml"}, data=xml_bytes)
    if r.status_code not in (200, 201, 204):
        r.raise_for_status()

# -------- Page /doc (interne) => exposée en /smart/doc
@doc_bp.get("/doc")
def doc_page():
    # simple page rendue par template
    return render_template("doc.html")

# -------- API
@doc_bp.get("/api/posts")
def api_list_posts():
    posts = fetch_posts()
    return jsonify({"posts": posts, "count": len(posts)})

@doc_bp.post("/api/posts")
def api_add_post():
    data = request.get_json(force=True) or {}
    content = data.get("content", "")
    posts = fetch_posts()
    posts.append(content)
    save_posts(posts)
    return jsonify({"ok": True, "count": len(posts)})

@doc_bp.post("/api/posts/insert")
def api_insert_post():
    data = request.get_json(force=True) or {}
    index = int(data.get("index", 1))
    content = data.get("content", "")
    posts = fetch_posts()
    index = max(1, min(index, len(posts) + 1))
    posts[index - 1:index - 1] = [content]
    save_posts(posts)
    return jsonify({"ok": True, "count": len(posts), "index": index})

@doc_bp.put("/api/posts/<int:index>")
def api_update_post(index: int):
    data = request.get_json(force=True) or {}
    content = data.get("content", "")
    posts = fetch_posts()
    if not (1 <= index <= len(posts)):
        return jsonify({"ok": False, "error": "index out of range"}), 400
    posts[index - 1] = content
    save_posts(posts)
    return jsonify({"ok": True})

@doc_bp.delete("/api/posts/<int:index>")
def api_delete_post(index: int):
    posts = fetch_posts()
    if not (1 <= index <= len(posts)):
        return jsonify({"ok": False, "error": "index out of range"}), 400
    del posts[index - 1]
    save_posts(posts)
    return jsonify({"ok": True, "count": len(posts)})
