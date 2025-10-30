"""
监控和性能追踪工具
"""

import time
import logging
from functools import wraps
from datetime import datetime

def monitor_performance(operation_name: str):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger(__name__)
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"PERF_{operation_name.upper()} | "
                    f"time={execution_time:.3f}s | "
                    f"success=True"
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"PERF_{operation_name.upper()} | "
                    f"time={execution_time:.3f}s | "
                    f"success=False | "
                    f"error={str(e)}"
                )
                raise
                
        return wrapper
    return decorator

def log_operation(operation_name: str):
    """操作日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(__name__)
            logger.info(f"START_{operation_name.upper()}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"COMPLETE_{operation_name.upper()}")
                return result
            except Exception as e:
                logger.error(f"FAILED_{operation_name.upper()} | error={str(e)}")
                raise
        return wrapper
    return decorator

# 简化的性能追踪器（如果没有logging配置）
class SimplePerformanceTracker:
    def __init__(self):
        self.operations = {}
    
    def track(self, operation_name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start
                    print(f"⏱️  {operation_name}: {duration:.3f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start
                    print(f"❌ {operation_name} failed after {duration:.3f}s: {e}")
                    raise
            return wrapper
        return decorator

# 创建全局追踪器实例
performance_tracker = SimplePerformanceTracker()
