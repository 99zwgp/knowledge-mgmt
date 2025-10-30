from abc import ABC, abstractmethod
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def ai_service_exception_handler(func):
    """AI服务异常处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"AI服务 {func.__name__} 执行成功，耗时: {execution_time:.2f}s")
            return result
        except Exception as e:
            logger.error(f"AI服务 {func.__name__} 执行失败: {str(e)}")
            # 返回降级结果，确保服务可用性
            return args[0]._fallback_result(*args, **kwargs)
    return wrapper

class BaseAIService(ABC):
    """AI服务基类 - 提供统一的接口和错误处理"""
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.initialized = False
        self.initialization_attempted = False
    
    @abstractmethod
    def initialize(self):
        """初始化服务"""
        pass
    
    @abstractmethod
    def process(self, text, **kwargs):
        """处理文本"""
        pass
    
    def ensure_initialized(self):
        """确保服务已初始化"""
        if not self.initialized and not self.initialization_attempted:
            self.initialization_attempted = True
            self.initialize()
    
    def _fallback_result(self, *args, **kwargs):
        """降级方案结果"""
        return {
            'success': False,
            'error': f'{self.service_name}服务暂时不可用',
            'fallback': True,
            'data': None
        }
    
    def health_check(self):
        """服务健康检查"""
        return {
            'service': self.service_name,
            'initialized': self.initialized,
            'status': 'healthy' if self.initialized else 'uninitialized'
        }
