#!/usr/bin/env python3
"""
最终验证脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def test_complete_import():
    """测试完整导入"""
    print("测试完整AI服务导入...")
    
    try:
        from app import create_app, db
        from app.services.ai import (
            classification_service,
            tagging_service,
            semantic_service, 
            recommendation_service,
            ai_management
        )
        
        print("✅ 应用导入成功")
        print("✅ 所有AI服务导入成功")
        
        # 测试服务实例
        print(f"分类服务: {classification_service.service_name}")
        print(f"标签服务: {tagging_service.service_name}") 
        print(f"语义服务: {semantic_service.service_name}")
        print(f"推荐服务: {recommendation_service.service_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """测试应用创建"""
    print("\n测试应用创建...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            print("✅ 应用创建成功")
            print("✅ 应用上下文正常")
            
            # 测试数据库连接
            from app import db
            result = db.session.execute('SELECT 1')
            print("✅ 数据库连接正常")
            
        return True
        
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 最终验证测试 ===\n")
    
    success = True
    success &= test_complete_import()
    success &= test_app_creation()
    
    if success:
        print("\n🎉 所有验证通过！系统可以正常启动")
        print("\n现在可以运行: python run.py")
    else:
        print("\n❌ 验证失败，需要进一步调试")
