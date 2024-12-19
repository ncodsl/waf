from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from os import path
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app and databases
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key_for_local_dev')
db = SQLAlchemy()
DB_NAME = "database.db"

# Get MongoDB URI from the environment variable
uri = os.getenv("MONGODB_URI")  # Fetches the MONGO_URI directly from the .env file

# Create a new MongoDB client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection to MongoDB
try:
    client.admin.command('ping')  # The 'admin' database is commonly used for testing the connection
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"An error occurred while pinging MongoDB: {e}")
    raise  # Raise the error if the MongoDB connection fails, to stop further initialization

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

# Dynamic port for Render or fallback to 5000 locally
port = os.getenv('PORT', 5000)  # Render sets PORT dynamically
app.run(debug=True, host='0.0.0.0', port=int(port))  # Ensuring the app listens on the correct port

def create_database(app):
    # Check if the database exists, if not, create it
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

# Add this at the bottom of __init__.py
__all__ = ['create_app', 'db']
