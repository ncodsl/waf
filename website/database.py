# This module handles database interactions using parameterized queries to prevent SQL injection attacks

import sqlite3

DB_NAME = 'Users.db'


# Initialize
def initialize_db():
   # Initialize the SQLite database.
   connection = sqlite3.connect(DB_NAME)
   cursor = connection.cursor()
   cursor.execute

# This module manages database interactions using parameterized queries to prevent SQL injection.

import sqlite3

DB_NAME = 'Users.db'

def initialize_db():
    """Initialize the SQLite database."""
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    connection.commit()
    connection.close()

def get_all_users():
    """Retrieve all users from the database."""
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('SELECT id, name, email FROM Users')
    users = cursor.fetchall()
    connection.close()
    return users

def insert_user(name, email):
    """Insert a new user into the database."""
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Using parameterized query to prevent SQL injection
    cursor.execute('INSERT INTO Users (name, email) VALUES (?, ?)', (name, email))
    connection.commit()
    connection.close()

