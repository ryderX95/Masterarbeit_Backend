from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database.database import db
from models.user import User 
import bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = User(username=username, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify({'message': 'Invalid credentials'}), 401
        
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({'token': access_token, 'role': user.role, 'points': user.points})

@auth_bp.route("/verify", methods=["GET"])
@jwt_required()
def verify_token():
    user_id = get_jwt_identity()
    return jsonify({"valid": True, "user_id": user_id}), 200