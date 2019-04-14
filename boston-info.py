# export FLASK_APP=boston-info.py
# debug mode: export FLASK_ENV=development
# flask run
from flask import Flask
app = Flask(__name__)


@app.route("/boston-info", methods=["GET", "POST"])
def boston_info():
    """This route renders a sample text."""
    # rendering text
    return 'Welcome to the Boston Info Slack Bot'
