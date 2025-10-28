from flask import Blueprint, request, jsonify
from app import db
from app.models import Document, Category
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
