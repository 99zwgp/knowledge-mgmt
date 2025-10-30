#!/usr/bin/env python3
"""
增强分类服务测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.ai.robust_classification_service import robust_classification_service

def test_enhanced_classification():
    """测试增强分类服务"""
    app = create_app()
    
    with app.app_context():
        # 初始化服务
        robust_classification_service.initialize()
        
        # 测试用例
        test_cases = [
            {
                'title': 'Python装饰器原理与实践',
                'content': '今天学习了Python装饰器的原理和使用方法，感觉对代码结构优化很有帮助。装饰器是Python中的重要特性，可以用于函数增强和代码复用。',
                'expected_category': '技术'
            },
            {
                'title': '项目会议总结',
                'content': '今天的项目会议讨论了下一阶段的开发计划和任务分配。需要完成用户管理模块和权限系统的开发。',
                'expected_category': '工作'
            },
            {
                'title': '机器学习学习笔记',
                'content': '学习了机器学习中的监督学习和无监督学习区别，整理了相关知识点和算法原理。',
                'expected_category': '学习'
            },
            {
                'title': '周末旅行计划',
                'content': '计划周末去爬山，感受大自然的美丽，放松心情重新出发。',
                'expected_category': '生活'
            }
        ]
        
        print("🧪 开始增强分类服务测试...")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            result = robust_classification_service.predict_category(
                test_case['title'], test_case['content']
            )
            
            print(f"测试用例 {i}: {test_case['title']}")
            print(f"  预测分类ID: {result['category_id']}")
            print(f"  置信度: {result['confidence']}")
            print(f"  使用方法: {result['method']}")
            print(f"  处理时间: {result.get('processing_time', 'N/A')}s")
            print()
        
        # 性能报告
        perf_report = robust_classification_service.get_performance_report()
        print("📊 性能报告:")
        for key, value in perf_report.items():
            print(f"  {key}: {value}")

if __name__ == '__main__':
    test_enhanced_classification()
