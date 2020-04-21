import os
from flask import send_from_directory, Blueprint
import logging


webui = Blueprint("webui", __name__, url_prefix="/")
log = logging.getLogger()


@webui.route("/", methods=["GET"])
def index():
    """
    Just send static index.html
    """
    return send_from_directory(
        os.path.sep.join([os.path.dirname(__file__), "static"]), "index.html",
    )
