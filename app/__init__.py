import os
from flask import Flask, send_from_directory
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Configure upload folder
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
    
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print(f"Upload folder path: {app.config['UPLOAD_FOLDER']}")
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

    # JWT Configuration
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    api = Api(app)

    from app.routes import auth, products
    api.add_resource(auth.UserRegistration, '/register')
    api.add_resource(auth.UserLogin, '/login')
    api.add_resource(auth.UserLogout, '/logout')
    api.add_resource(products.ProductList, '/products')
    api.add_resource(products.ProductResource, '/products/<int:product_id>')

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500

    return app