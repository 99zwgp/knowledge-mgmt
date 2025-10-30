#!/usr/bin/env python3
"""
最小化测试 - 验证基本导入和功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_basic_imports():
    """测试基本导入"""
    print("测试基本导入...")
    
    try:
        from app.services.ai.base_service import BaseAIService, ai_service_exception_handler
        print("✅ BaseAIService 导入成功")
        print("✅ ai_service_exception_handler 导入成功")
        return True
    except Exception as e:
        print(f"❌ 基础导入失败: {e}")
        return False

def test_service_imports():
    """测试服务导入"""
    print("\n测试服务导入...")
    
    try:
        from app.services.ai.classification_service import classification_service
        print("✅ classification_service 导入成功")
    except Exception as e:
        print(f"❌ 分类服务导入失败: {e}")
        return False
        
    try:
        from app.services.ai.tagging_service import tagging_service
        print("✅ tagging_service 导入成功")
    except Exception as e:
        print(f"❌ 标签服务导入失败: {e}")
        return False
        
    return True

def test_service_creation():
    """测试服务创建"""
    print("\n测试服务创建...")
    
    try:
        from app.services.ai.classification_service import classification_service
        from app.services.ai.tagging_service import tagging_service
        
        print(f"✅ 分类服务名称: {classification_service.service_name}")
        print(f"✅ 标签服务名称: {tagging_service.service_name}")
        print(f"✅ 分类服务初始化状态: {classification_service.initialized}")
        print(f"✅ 标签服务初始化状态: {tagging_service.initialized}")
        
        return True
    except Exception as e:
        print(f"❌ 服务创建测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== AI服务最小化测试 ===\n")
    
    success = True
    success &= test_basic_imports()
    success &= test_service_imports() 
    success &= test_service_creation()
    
    if success:
        print("\n🎉 所有测试通过！AI服务基本功能正常")
    else:
        print("\n❌ 部分测试失败，需要进一步调试")
