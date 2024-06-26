import os

from dotenv import load_dotenv

from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_jwt_extended import JWTManager
from flasgger import Swagger


# Load .env
load_dotenv()

# Extension's Init
engine = create_engine(os.getenv('DATABASE_URL'))
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Flask config from env
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

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
    from .auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
