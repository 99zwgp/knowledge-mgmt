from flask import Blueprint, request, jsonify
from app.models import Document, Category
from app import db
import traceback
from app.utils.monitoring import monitor_performance, log_operation

# 使用增强版分类服务
from app.services.ai.robust_classification_service import robust_classification_service

document_ai_bp = Blueprint('document_ai', __name__)

@document_ai_bp.route('/api/ai/documents', methods=['POST'])
@monitor_performance("document_creation_ai")
@log_operation("create_document_with_ai")
def create_document_with_ai():
    """创建文档并使用AI自动处理"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title or not content:
            return jsonify({'success': False, 'error': 'Title and content are required'}), 400
        
        # 使用增强版AI分类服务
        category_result = robust_classification_service.process(
            content, title=title, content=content
        )
        
        # 创建文档
        new_document = Document(
            title=title,
            content=content,
            category_id=category_result.get('category_id'),
            ai_processed=True
        )
        
        db.session.add(new_document)
        db.session.commit()
        
        # 构建响应
        response_data = {
            'success': True,
            'document_id': new_document.id,
            'ai_processing': {
                'category_prediction': {
                    'category_id': category_result.get('category_id'),
                    'confidence': category_result.get('confidence'),
                    'method': category_result.get('method')
                },
                'performance': category_result.get('processing_time')
            }
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating document: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@document_ai_bp.route('/api/ai/documents/<int:doc_id>/reclassify', methods=['POST'])
@monitor_performance("document_reclassification")
def reclassify_document(doc_id):
    """重新分类文档"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        # 使用增强版AI分类服务重新分类
        category_result = robust_classification_service.process(
            document.content, title=document.title, content=document.content
        )
        
        # 更新文档分类
        document.category_id = category_result.get('category_id')
        document.ai_processed = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'document_id': document.id,
            'new_category_id': category_result.get('category_id'),
            'confidence': category_result.get('confidence'),
            'method': category_result.get('method'),
            'processing_time': category_result.get('processing_time')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@document_ai_bp.route('/api/ai/documents/classify-text', methods=['POST'])
@monitor_performance("text_classification")
def classify_text():
    """仅对文本进行分类（不保存文档）"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        title = data.get('title', '').strip()
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        # 使用增强版AI分类服务
        category_result = robust_classification_service.process(
            text, title=title, content=text
        )
        
        # 获取分类名称
        category_name = None
        if category_result.get('category_id'):
            category = Category.query.get(category_result['category_id'])
            category_name = category.name if category else None
        
        return jsonify({
            'success': True,
            'classification': {
                'category_id': category_result.get('category_id'),
                'category_name': category_name,
                'confidence': category_result.get('confidence'),
                'method': category_result.get('method'),
                'processing_time': category_result.get('processing_time'),
                'algorithm_details': category_result.get('algorithm_details', {})
            },
            'performance': robust_classification_service.get_performance_report()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@document_ai_bp.route('/api/ai/classification/performance', methods=['GET'])
def get_classification_performance():
    """获取分类服务性能报告"""
    try:
        performance_report = robust_classification_service.get_performance_report()
        
        return jsonify({
            'success': True,
            'service': 'enhanced_classification',
            'performance': performance_report
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@document_ai_bp.route('/api/ai/classification/clear-cache', methods=['POST'])
def clear_classification_cache():
    """清空分类缓存"""
    try:
        robust_classification_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Classification cache cleared successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
