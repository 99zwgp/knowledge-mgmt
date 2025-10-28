from flask import Blueprint, request, jsonify
from app import db
from app.models import Document, Category
from app.utils.helpers import validate_document_data, validate_ids, format_response
from datetime import datetime
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify({'message': 'Knowledge Management System API', 'status': 'running'})

@main_bp.route('/api/documents', methods=['GET'])
def get_documents():
    """获取文档列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    documents = Document.query.order_by(Document.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'documents': [doc.to_dict() for doc in documents.items],
        'total': documents.total,
        'pages': documents.pages,
        'current_page': page
    })

@main_bp.route('/api/documents', methods=['POST'])
def create_document():
    """创建新文档"""
    try:
        data = request.get_json()
        
        # 基础验证
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({'error': '标题和内容不能为空'}), 400
        
        # 创建文档
        document = Document(
            title=data['title'],
            content=data['content'],
            file_type=data.get('file_type', 'text'),
            tags=data.get('tags', [])
        )
        
        # 简单的分类逻辑（后续用AI增强）
        if '代码' in data['content'] or '编程' in data['content']:
            tech_category = Category.query.filter_by(name='技术').first()
            if tech_category:
                document.category_id = tech_category.id
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'message': '文档创建成功',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建文档失败: {str(e)}'}), 500

@main_bp.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """获取单个文档详情"""
    document = Document.query.get_or_404(doc_id)
    return jsonify({'document': document.to_dict()})

@main_bp.route('/api/documents/<int:doc_id>/detail', methods=['GET'])
def get_document_detail(doc_id):
    """获取文档完整详情（包含完整内容）"""
    document = Document.query.get_or_404(doc_id)
    
    # 完整的文档详情，不截断内容
    detail_data = {
        'id': document.id,
        'title': document.title,
        'content': document.content,  # 完整内容
        'file_type': document.file_type,
        'tags': document.tags or [],
        'created_at': document.created_at.isoformat() if document.created_at else None,
        'updated_at': document.updated_at.isoformat() if document.updated_at else None,
    }
    
    if document.category:
        detail_data['category'] = {
            'id': document.category.id,
            'name': document.category.name
        }
    
    return jsonify({
        'document': detail_data
    })

@main_bp.route('/api/documents/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    """更新文档信息"""
    try:
        document = Document.query.get_or_404(doc_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 使用工具函数验证数据
        errors = validate_document_data(data, is_update=True)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        # 更新允许修改的字段
        updatable_fields = ['title', 'content', 'file_type', 'tags']
        updated = False
        
        for field in updatable_fields:
            if field in data and getattr(document, field) != data[field]:
                setattr(document, field, data[field])
                updated = True
        
        if updated:
            document.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({
                'message': '文档更新成功',
                'document': document.to_dict()
            })
        else:
            return jsonify({
                'message': '文档内容未变化',
                'document': document.to_dict()
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新文档失败: {str(e)}'}), 500

@main_bp.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """删除文档"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'message': '文档删除成功',
            'deleted_id': doc_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除文档失败: {str(e)}'}), 500

@main_bp.route('/api/documents/batch-delete', methods=['POST'])
def batch_delete_documents():
    """批量删除文档"""
    try:
        data = request.get_json()
        
        if not data or not data.get('ids'):
            return jsonify({'error': '请提供要删除的文档ID列表'}), 400
        
        ids = data['ids']
        
        # 验证ID格式
        is_valid, error_msg = validate_ids(ids)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 查询存在的文档
        documents = Document.query.filter(Document.id.in_(ids)).all()
        found_ids = [doc.id for doc in documents]
        
        # 检查是否有不存在的ID
        not_found_ids = set(ids) - set(found_ids)
        
        if documents:
            for document in documents:
                db.session.delete(document)
            db.session.commit()
        
        response_data = {
            'message': f'成功删除 {len(documents)} 个文档',
            'deleted_ids': found_ids,
        }
        
        if not_found_ids:
            response_data['warning'] = f'以下ID未找到: {list(not_found_ids)}'
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量删除失败: {str(e)}'}), 500

@main_bp.route('/api/search/advanced', methods=['GET'])
def advanced_search():
    """高级搜索接口"""
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'relevance')
        search_mode = request.args.get('search_mode', 'or')  # 新增搜索模式参数
        
        # 验证参数
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        if search_mode not in ['or', 'and']:
            search_mode = 'or'
        
        from app.services.search_service import search_service
        search_result = search_service.advanced_search(
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            search_mode=search_mode  # 传递搜索模式
        )
        
        return jsonify(search_result)
        
    except Exception as e:
        return jsonify({
            'error': f'搜索失败: {str(e)}',
            'query': request.args.get('q', ''),
            'results': [],
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': 0,
                'pages': 0
            }
        }), 500

@main_bp.route('/api/search/suggestions', methods=['GET'])
def search_suggestions():
    """搜索建议接口"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 5, type=int)
        
        from app.services.search_service import search_service
        suggestions = search_service.search_suggestions(query, limit)
        
        return jsonify({
            'query': query,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({
            'error': f'获取搜索建议失败: {str(e)}',
            'suggestions': []
        }), 500

@main_bp.route('/api/search/stats', methods=['GET'])
def search_stats():
    """搜索统计信息"""
    try:
        from app.models import Document, Category
        
        total_documents = Document.query.count()
        total_categories = Category.query.count()
        
        # 最近7天创建的文档（示例）
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_documents = Document.query.filter(
            Document.created_at >= week_ago
        ).count()
        
        return jsonify({
            'total_documents': total_documents,
            'total_categories': total_categories,
            'recent_documents_7d': recent_documents,
            'last_updated': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'获取统计信息失败: {str(e)}'
        }), 500

@main_bp.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    categories = Category.query.all()
    return jsonify({'categories': [cat.to_dict() for cat in categories]})

@main_bp.route('/api/categories', methods=['POST'])
def create_category():
    """创建分类"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': '分类名称不能为空'}), 400
        
        category = Category(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': '分类创建成功',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建分类失败: {str(e)}'}), 500

@main_bp.route('/api/search')
def search_documents():
    """简单搜索文档"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    # 简单的内容搜索（后续用AI增强）
    documents = Document.query.filter(
        Document.title.contains(query) | Document.content.contains(query)
    ).order_by(Document.created_at.desc()).limit(10).all()
    
    return jsonify({
        'query': query,
        'results': [doc.to_dict() for doc in documents],
        'count': len(documents)
    })
