# migrations_setup.py - Database Migration Setup

from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from models import db
from app_enhanced import create_app
import os

def setup_migrations():
    """Initialize Flask-Migrate for the project"""
    app = create_app()
    
    with app.app_context():
        # Initialize migration repository if it doesn't exist
        if not os.path.exists('migrations'):
            print("Initializing migration repository...")
            init()
            print("Migration repository initialized.")
        
        # Create initial migration
        print("Creating initial migration...")
        migrate(message='Initial migration')
        print("Initial migration created.")
        
        # Apply migrations
        print("Applying migrations...")
        upgrade()
        print("Migrations applied successfully.")

if __name__ == '__main__':
    setup_migrations()
