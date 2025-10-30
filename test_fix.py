#!/usr/bin/env python3
"""
验证AI服务导入问题的修复
"""

try:
    from app.services.ai.base_service import ai_service_exception_handler
    from app.services.ai.classification_service import classification_service
    from app.services.ai.tagging_service import tagging_service
    
    print("✅ AI服务导入成功!")
    print("✅ 装饰器导入成功!")
    
    # 测试基本功能
    print("\n测试分类服务基本功能...")
    try:
        result = classification_service.process("测试文本", title="测试标题")
        print("✅ 分类服务基本功能正常")
    except Exception as e:
        print(f"❌ 分类服务错误: {e}")
    
    print("\n测试标签服务基本功能...")
    try:
        result = tagging_service.process("测试文本内容", title="测试标题")
        print("✅ 标签服务基本功能正常")
    except Exception as e:
        print(f"❌ 标签服务错误: {e}")
        
except ImportError as e:
    print(f"❌ 导入失败: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")
