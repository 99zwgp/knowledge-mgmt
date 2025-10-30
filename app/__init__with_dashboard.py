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
    from app.routes_ai import ai_bp
    from app.routes_document_ai_enhanced import document_ai_bp
    from app.routes_dashboard import dashboard_bp  # 新增看板路由
    
    app.register_blueprint(main_bp)
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(document_ai_bp, url_prefix='/api/ai')
    app.register_blueprint(dashboard_bp)  # 看板路由使用根路径
    
    # 使用应用上下文进行AI服务初始化
    with app.app_context():
        try:
            from app.services.ai.management_service_enhanced import ai_management
            init_result = ai_management.initialize_all_services()
            print("AI服务初始化结果:", init_result)
        except Exception as e:
            print(f"AI服务初始化警告: {e}")
    
    return app
