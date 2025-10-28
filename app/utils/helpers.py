import json
from datetime import datetime
from flask import jsonify
import re

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

def highlight_text(text, keywords, max_length=200):
    """在文本中高亮显示关键词"""
    if not text or not keywords:
        return text[:max_length] + '...' if len(text) > max_length else text
    
    # 转义关键词中的特殊字符
    escaped_keywords = [re.escape(keyword) for keyword in keywords]
    
    # 创建高亮模式
    pattern = '|'.join(escaped_keywords)
    
    try:
        # 高亮处理
        highlighted = re.sub(
            f'({pattern})', 
            r'<mark>\1</mark>', 
            text, 
            flags=re.IGNORECASE
        )
        
        # 截断处理
        if len(highlighted) > max_length:
            # 找到第一个高亮标签的位置
            mark_pos = highlighted.find('<mark>')
            if mark_pos != -1 and mark_pos > 50:
                start = max(0, mark_pos - 50)
                highlighted = '...' + highlighted[start:start + max_length] + '...'
            else:
                highlighted = highlighted[:max_length] + '...'
        
        return highlighted
    except:
        return text[:max_length] + '...' if len(text) > max_length else text

def calculate_relevance(title, content, tags, query, keywords):
    """计算文档与查询的相关度分数"""
    score = 0
    
    # 标题匹配权重最高
    for keyword in keywords:
        if keyword.lower() in title.lower():
            score += 10
        if keyword.lower() in content.lower():
            score += 3
        if tags and any(keyword.lower() in str(tag).lower() for tag in tags):
            score += 5
    
    return score

def extract_search_keywords(query):
    """从搜索查询中提取关键词"""
    if not query:
        return []
    
    # 简单的关键词分割，可以后续用更智能的方法
    keywords = query.strip().split()
    
    # 过滤空关键词和短词
    keywords = [kw for kw in keywords if len(kw) > 1]
    
    return keywords
