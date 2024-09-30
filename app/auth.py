from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User
from . import db_session

from flasgger import swag_from

auth = Blueprint('auth', __name__)


@auth.route('/users', methods=['GET'])
@jwt_required()
@swag_from({
    'security': [{
        'Bearer': []
    }],
    'responses': {
        200: {
            'description': 'A list of users',
            'examples': {
                'application/json': [
                    {'id': 1, 'username': 'john', 'email': 'john@example.com'},
                    {'id': 2, 'username': 'jane', 'email': 'jane@example.com'}
                ]
            }
        }
    }
})
def get_users():
    current_user_id = get_jwt_identity()
    users = db_session.query(User).all()
    return jsonify(
        [
            {'id': user.id, 'username': user.username, 'email': user.email} for user in users
        ]
    )


@auth.route('/register', methods=['POST'])
@swag_from({
    'security': [{
        'Bearer': []
    }],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        201: {'description': 'User registered successfully'},
        400: {'description': 'Username or email already exists'}
    }
})
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if db_session.query(User).filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    if db_session.query(User).filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db_session.add(new_user)
    db_session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@auth.route('/login', methods=['POST'])
@swag_from({
    'security': [{
        'Bearer': []
    }],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {'description': 'Login successful, returns access token'},
        401: {'description': 'Invalid username or password'}
    }
})
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = db_session.query(User).filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200
