"""
AI服务管理模块
提供AI服务的统一管理和监控
"""
import time
from app.services.ai import (
    classification_service, 
    tagging_service, 
    semantic_service, 
    recommendation_service
)

class AIManagementService:
    """AI服务管理"""
    
    def __init__(self):
        self.services = {
            'classification': classification_service,
            'tagging': tagging_service,
            'semantic': semantic_service,
            'recommendation': recommendation_service
        }
    
    def initialize_all_services(self):
        """初始化所有AI服务"""
        results = {}
        for name, service in self.services.items():
            try:
                service.ensure_initialized()
                results[name] = {
                    'status': 'initialized' if service.initialized else 'failed',
                    'service_name': service.service_name
                }
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'service_name': service.service_name
                }
        
        return {
            'success': True,
            'initialization_results': results,
            'timestamp': time.time()
        }
    
    def health_check(self):
        """检查所有AI服务健康状态"""
        health_status = {}
        for name, service in self.services.items():
            health_status[name] = service.health_check()
        
        # 总体健康状态
        all_healthy = all(service.initialized for service in self.services.values())
        
        return {
            'overall_status': 'healthy' if all_healthy else 'degraded',
            'services': health_status,
            'timestamp': time.time()
        }
    
    def get_service_stats(self):
        """获取AI服务统计信息"""
        stats = {}
        for name, service in self.services.items():
            stats[name] = {
                'service_name': service.service_name,
                'initialized': service.initialized,
                'initialization_attempted': service.initialization_attempted
            }
        
        return {
            'stats': stats,
            'total_services': len(self.services),
            'initialized_services': sum(1 for s in self.services.values() if s.initialized)
        }

# 创建全局管理实例
ai_management = AIManagementService()
