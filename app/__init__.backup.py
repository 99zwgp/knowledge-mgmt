from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # 使用应用上下文进行AI服务初始化
    with app.app_context():
        try:
            from app.services.ai import ai_management
            init_result = ai_management.initialize_all_services()
            print("AI服务初始化结果:", init_result)
        except Exception as e:
            print(f"AI服务初始化警告: {e}")
            # 不阻止应用启动，AI服务会按需初始化
    
    return app
