import json
from datetime import datetime
from flask import jsonify

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

def validate_document_data(data, is_update=False):
    """验证文档数据"""
    errors = []
    
    if not is_update and not data.get('title', '').strip():
        errors.append('标题不能为空')
    
    if not is_update and not data.get('content', '').strip():
        errors.append('内容不能为空')
    
    if 'title' in data and len(data.get('title', '')) > 255:
        errors.append('标题长度不能超过255个字符')
    
    return errors

def validate_ids(ids):
    """验证ID列表"""
    if not isinstance(ids, list):
        return False, "IDs应该是列表格式"
    
    if not all(isinstance(i, int) and i > 0 for i in ids):
        return False, "所有ID应该是正整数"
    
    return True, ""
