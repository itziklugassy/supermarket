from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app import db

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='This field cannot be blank', required=True)
        parser.add_argument('email', help='This field cannot be blank', required=True)
        parser.add_argument('password', help='This field cannot be blank', required=True)
        data = parser.parse_args()

        if User.query.filter_by(username=data['username']).first():
            return {'message': 'User already exists'}, 400

        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already in use'}, 400

        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        try:
            db.session.add(new_user)
            db.session.commit()
            access_token = create_access_token(identity=new_user.id)
            return {'message': 'User created successfully', 'access_token': access_token}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Something went wrong', 'error': str(e)}, 500

class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='This field cannot be blank', required=True)
        parser.add_argument('password', help='This field cannot be blank', required=True)
        data = parser.parse_args()

        print(f"Received login attempt for username: {data['username']}")

        user = User.query.filter_by(username=data['username']).first()
        if not user:
            print("User not found.")
            return {'message': 'Invalid credentials: user not found'}, 401

        print(f"User found: {user.username}, checking password...")

        if not user.check_password(data['password']):
            print("Incorrect password.")
            return {'message': 'Invalid credentials: incorrect password'}, 401

        print("Login successful.")
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token, 'message': 'Login successful'}, 200

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        return {'message': 'Successfully logged out'}, 200