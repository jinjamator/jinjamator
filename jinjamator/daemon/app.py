from flask import Flask

app = Flask(__name__, static_folder=None)


@app.after_request
def apply_header_security(response):
    response.headers["X-Frame-Options"] = "DENY"

    return response
