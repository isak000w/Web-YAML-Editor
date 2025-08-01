"""
Configuration settings for the YAML Editor application.
"""
import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database configuration (using SQLite database in base directory)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Enable debug mode (for development)
DEBUG = True

# Allowed file extensions for YAML files
ALLOWED_EXTENSIONS = {'.yaml', '.yml'}

# JSON Schema for validation (None or a dict defining the schema)
SCHEMA = None  # e.g., set to a dict with JSON schema if needed for validation

# Timestamp format for displaying version history
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"