import sys
import logging

logging.basicConfig(stream=sys.stderr)

# Ajouter le dossier smart au sys.path
sys.path.insert(0, "/var/www/html/smart")

from app import app as application