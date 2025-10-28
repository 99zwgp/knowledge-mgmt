import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'knowledge_user'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '2022fjm'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'knowledge_mgmt'
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis配置 - 修复密码问题
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') or 'yourpassword'
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@localhost:6379/0'
    
    # 文件上传
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
