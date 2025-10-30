from flask import Blueprint, render_template, jsonify
from app.models import Document, Category
from app import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """显示主看板页面"""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/dashboard/stats')
def get_dashboard_stats():
    """获取看板统计信息"""
    try:
        doc_count = Document.query.count()
        category_count = Category.query.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'document_count': doc_count,
                'category_count': category_count,
                'ai_services': 5  # 假设有5个AI服务
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/documents/recent')
def get_recent_documents():
    """获取最近文档"""
    try:
        recent_docs = Document.query.order_by(Document.created_at.desc()).limit(10).all()
        
        documents = []
        for doc in recent_docs:
            documents.append({
                'id': doc.id,
                'title': doc.title,
                'content_preview': doc.content[:100] + '...' if len(doc.content) > 100 else doc.content,
                'category_id': doc.category_id,
                'created_at': doc.created_at.isoformat() if doc.created_at else None
            })
        
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
