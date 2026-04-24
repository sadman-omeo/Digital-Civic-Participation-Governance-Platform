"""
Production configuration for Vercel deployment
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_key_change_in_production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Database
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///voting_system.db"
    
    # Upload configuration
    UPLOAD_FOLDER = "static/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Session
    SESSION_TYPE = "filesystem"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration for Vercel"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}
