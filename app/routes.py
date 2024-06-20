import sqlalchemy
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, db_session

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def index_view():
    # current_user_id = get_jwt_identity()
    # users = User.query.all()
    users = db_session.query(User).all()

    return jsonify(
        message='Welcome to Flask-Simple-API! <3!',
        more='Ahora con auto-reload dentro del contenedor.',
        users=[x.username for x in users]
    )
