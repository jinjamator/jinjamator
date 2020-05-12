import os
from flask import send_from_directory, Blueprint
import logging
from jinjamator.daemon.aaa import aaa_providers

webui = Blueprint("webui", __name__, url_prefix="/")
log = logging.getLogger()


@webui.route("/index.html", methods=["GET"])
@webui.route("/", methods=["GET"])
def index():
    """
    Just send static index.html
    """
    return send_from_directory(
        os.path.sep.join([os.path.dirname(__file__), "static"]), "index.html"
    )


@webui.route("/login.html", methods=["GET"])
def login():
    """
    Just send static login.html
    """
    return send_from_directory(
        os.path.sep.join([os.path.dirname(__file__), "static"]), "login.html"
    )
