import json
from datetime import datetime

def format_response(data=None, message="", status="success", code=200):
    """统一响应格式"""
    response = {
        "status": status,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return response, code

def validate_document_data(data):
    """验证文档数据"""
    errors = []
    
    if not data.get('title', '').strip():
        errors.append('标题不能为空')
    
    if not data.get('content', '').strip():
        errors.append('内容不能为空')
    
    if len(data.get('title', '')) > 255:
        errors.append('标题长度不能超过255个字符')
    
    return errors
