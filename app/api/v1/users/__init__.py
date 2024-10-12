from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flasgger import swag_from

from app.models import User
from app.db import db_session


def fetch_all_users():
    users = db_session.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "status": user.status,
            "url_identifier": user.url_identifier
        } for user in users
    ]


def fetch_user_by_id(user_id):
    user = db_session.query(User).filter_by(id=user_id).first()
    if user:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    return None


def create_user(username, email, password, bio):
    if db_session.query(User).filter_by(username=username).first():
        return {"error": "Username already exists"}

    if db_session.query(User).filter_by(email=email).first():
        return {"error": "Email already exists"}

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    new_user.bio = bio
    new_user.status = 1
    new_user.url_identifier = f'/u/{username}'

    db_session.add(new_user)
    db_session.commit()

    return {"message": "User created successfully"}


users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['User'],
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
    """Get all users"""
    users = fetch_all_users()
    return jsonify(users), 200


@users_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = fetch_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"message": "User not found"}), 404


@users_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['User'],
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
                    'password': {'type': 'string'},
                    'bio': {'type': 'string'}
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
def create_new_user():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    bio = data.get('bio')

    if not username or not email or not password:
        return jsonify({"message": "Missing fields"}), 400

    result = create_user(username, email, password, bio)
    if result.get('error'):
        return jsonify(result), 400

    return jsonify({"message": "User created successfully"}), 201

@users_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['User'],
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
                    'email': {'type': 'string'},
                    'bio': {'type': 'string'}
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
def put_user():
    current_user_id = get_jwt_identity()
    user = db_session.query(User).filter_by(id=current_user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    _perform_update = False
    if data.get('email'):
        user.email = data.get('email')
        _perform_update = True
    if data.get('bio'):
        user.bio = data.get('bio')
        _perform_update = True

    if _perform_update:
        db_session.add(user)
        db_session.commit()
        return jsonify({"message": "User updated successfully"}), 200

    return jsonify({"message": "User not updated?"}), 200


@users_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'security': [],
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

@users_bp.route('/me', methods=['GET'])
@jwt_required()
@swag_from({
    'security': [{
        'Bearer': []
    }],
    'tags': ['User'],
    # 'parameters': [],
    'responses': {
        200: {'description': 'Returns the current user information'},
        401: {'description': 'Unauthorized'}
    }
})
def get_me():
    current_user_id = get_jwt_identity()
    user = db_session.query(User).filter_by(id=current_user_id).first()
    if user:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "status": user.status,
            "url_identifier": user.url_identifier
        }
    return None
