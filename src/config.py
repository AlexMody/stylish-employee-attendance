import os
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database configuration
    if os.environ.get('DATABASE_URL'):
        # Parse the DATABASE_URL for PostgreSQL
        url = urlparse(os.environ.get('DATABASE_URL'))
        # Convert postgres:// to postgresql://
        if url.scheme == 'postgres':
            url = url._replace(scheme='postgresql')
        SQLALCHEMY_DATABASE_URI = url.geturl()
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///attendance.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 