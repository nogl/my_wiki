import os
import sys

from dotenv import load_dotenv
from loguru import logger

from flask import Flask

from flask_jwt_extended import JWTManager
from flasgger import Swagger

from app.commands import db_cli

logger.remove(0)
logger.add(sys.stderr, level="TRACE", format="<level><b>{time:YYYY_MM_DD-HH:mm:ss} | {level}</b> | {message}</level>")

# Load develop.env
load_dotenv()

jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Flask config from env
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    logger.info(f'Start Flask APP - {os.getenv('DATABASE_URL')}')

    # Flask extensions
    jwt.init_app(app)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },

        "security": [
            {
                "Bearer": []
            }
        ]
    }

    Swagger(app, config=swagger_config)

    from .routes import main
    app.register_blueprint(main)

    from .api.v1.users import users_bp
    app.register_blueprint(users_bp)

    with app.app_context():
        app.cli.add_command(db_cli)
    return app
