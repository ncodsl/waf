from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.auth import MECHANISMS
import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ee57afdfa96ac3c926796cc1228d509c'
    
    # 1. Setup MongoDB with explicit SCRAM-SHA-256 authentication
    try:
        logger.info("Attempting MongoDB connection with SCRAM-SHA-256...")
        
        # MongoDB URI with explicit SCRAM-SHA-256
        MONGODB_URI = "mongodb://churchillokonkwo:u8ZQ2Um6ZgwpG42K@waf-cluster.kv58j.mongodb.net/?authMechanism=SCRAM-SHA-256&authSource=admin&retryWrites=true&w=majority&appName=WAF-Cluster"
        
        mongo_client = MongoClient( MONGODB_URI )
        
        # Test connection
        logger.info("Testing MongoDB connection...")
        mongo_client.admin.command('ping')
        
        # Store mongo client in app config
        app.config['mongo_client'] = mongo_client
        logger.info("MongoDB connection successful!")
        
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        logger.error("Full error details:", exc_info=True)
        raise
        
    # 2. Setup SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # 3. Register blueprints
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    from .models import User, Note
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

# Add this at the bottom of __init__.py
__all__ = ['create_app', 'db']
