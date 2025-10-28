from app.models import Document
from app.utils.helpers import highlight_text, calculate_relevance, extract_search_keywords
from flask_sqlalchemy import Pagination
from sqlalchemy import or_, and_

class SearchService:
    def __init__(self):
        pass
    
    def advanced_search(self, query, page=1, per_page=10, sort_by='relevance', search_mode='or'):
        """高级搜索功能
        
        Args:
            search_mode: 'or' - 任意关键词匹配, 'and' - 所有关键词匹配
        """
        if not query or not query.strip():
            return self._empty_search_result(page, per_page)
        
        # 提取搜索关键词
        keywords = extract_search_keywords(query)
        
        # 构建基础查询
        base_query = Document.query
        
        # 多字段搜索条件
        if keywords:
            if search_mode == 'and':
                # AND模式：必须包含所有关键词
                search_conditions = []
                for keyword in keywords:
                    condition = (
                        Document.title.contains(keyword) |
                        Document.content.contains(keyword) |
                        Document.tags.contains([keyword])
                    )
                    search_conditions.append(condition)
                
                if search_conditions:
                    base_query = base_query.filter(and_(*search_conditions))
            else:
                # OR模式：包含任意关键词（默认）
                or_conditions = []
                for keyword in keywords:
                    condition = (
                        Document.title.contains(keyword) |
                        Document.content.contains(keyword) |
                        Document.tags.contains([keyword])
                    )
                    or_conditions.append(condition)
                
                if or_conditions:
                    base_query = base_query.filter(or_(*or_conditions))
        
        # 获取总数
        total = base_query.count()
        
        # 排序处理
        if sort_by == 'relevance':
            # 按相关度排序（暂时按创建时间，后续可优化）
            base_query = base_query.order_by(Document.created_at.desc())
        elif sort_by == 'date_asc':
            base_query = base_query.order_by(Document.created_at.asc())
        elif sort_by == 'date_desc':
            base_query = base_query.order_by(Document.created_at.desc())
        elif sort_by == 'title':
            base_query = base_query.order_by(Document.title.asc())
        
        # 分页
        documents = base_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 处理搜索结果
        processed_docs = []
        for doc in documents.items:
            doc_dict = doc.to_dict()
            
            # 计算相关度
            relevance_score = calculate_relevance(
                doc.title, doc.content, doc.tags, query, keywords
            )
            
            # 添加高亮
            doc_dict['highlighted_title'] = highlight_text(doc.title, keywords)
            doc_dict['highlighted_content'] = highlight_text(doc.content, keywords)
            doc_dict['relevance_score'] = relevance_score
            
            processed_docs.append(doc_dict)
        
        # 按相关度重新排序（如果适用）
        if sort_by == 'relevance':
            processed_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            'query': query,
            'keywords': keywords,
            'results': processed_docs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': documents.pages
            },
            'stats': {
                'total_matches': total,
                'keywords_count': len(keywords),
                'search_mode': search_mode
            }
        }
    
    def _empty_search_result(self, page, per_page):
        """空搜索查询的结果"""
        return {
            'query': '',
            'keywords': [],
            'results': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': 0,
                'pages': 0
            },
            'stats': {
                'total_matches': 0,
                'keywords_count': 0,
                'search_mode': 'or'
            }
        }
    
    def search_suggestions(self, query, limit=5):
        """搜索建议"""
        if not query or len(query) < 2:
            return []
        
        # 简单的标题匹配建议
        suggestions = Document.query.filter(
            Document.title.contains(query)
        ).limit(limit).all()
        
        return [doc.title for doc in suggestions]

# 创建全局搜索服务实例
search_service = SearchService()
