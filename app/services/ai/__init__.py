"""
AI服务模块
提供智能文档处理、分类、标签生成、语义搜索和内容推荐功能
"""

from .base_service import BaseAIService, ai_service_exception_handler
from .classification_service import classification_service
from .tagging_service import tagging_service
from .semantic_service import semantic_service
from .recommendation_service import recommendation_service
from .management_service import ai_management
from .robust_classification_service import robust_classification_service

__all__ = [
    'BaseAIService',
    'ai_service_exception_handler',
    'classification_service',
    'tagging_service', 
    'semantic_service',
    'recommendation_service',
    'ai_management',
    'robust_classification_service'  # 新增增强分类服务
]

print("AI服务模块导入完成")
