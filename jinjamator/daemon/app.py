from flask import Flask

app = Flask(__name__, static_folder="./webui/static")
