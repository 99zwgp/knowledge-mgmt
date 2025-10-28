from app import create_app, db
from app.models import Category

def init_categories():
    app = create_app()
    
    with app.app_context():
        # 创建默认分类
        default_categories = [
            {'name': '技术', 'description': '编程、算法、架构等技术相关内容'},
            {'name': '学习', 'description': '学习笔记、心得体会'},
            {'name': '生活', 'description': '日常生活记录'},
            {'name': '工作', 'description': '工作相关文档'},
        ]
        
        for cat_data in default_categories:
            if not Category.query.filter_by(name=cat_data['name']).first():
                category = Category(**cat_data)
                db.session.add(category)
                print(f"创建分类: {cat_data['name']}")
        
        db.session.commit()
        print("初始化数据完成！")

if __name__ == '__main__':
    init_categories()
