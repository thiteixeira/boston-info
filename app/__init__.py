from flask_api import FlaskAPI
from config.env import app_env
from app.utils.slackhelper import SlackHelper


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=False)
    app.config.from_object(app_env[config_name])
    app.config.from_pyfile('../config/env.py')

    @app.route("/", methods=["GET"])
    def home():
        """This route renders a sample text."""
        # rendering text
        return 'Welcome to the Boston Info Slack Bot'

    return app
