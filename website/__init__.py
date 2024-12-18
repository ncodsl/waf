from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import pyMongo
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from os import path

# Load environment variables from .env file
load_dotenv()

# Initialize SQLAlchemy and MongoDB
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ee57afdfa96ac3c926796cc1228d509c'

    # 1. Setup MongoDB with Flask-PyMongo
    app.config["MONGO_URI"] = os.getenv("MONGODB_URI")  # Mongo URI from environment variable
    mongo = PyMongo(app)
    
    # Test MongoDB connection
    try:
        collections = mongo.db.list_collection_names()
        print("MongoDB collections: ", collections)
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        raise

    # 2. Setup SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # SQLite database URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # 3. Register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # 4. Initialize models and create the database (if it doesn't exist)
    from .models import User, Note
    with app.app_context():
        db.create_all()

    # 5. Setup login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    # Check if the database exists, if not, create it
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

# Add this at the bottom of __init__.py
__all__ = ['create_app', 'db']
