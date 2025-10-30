from flask import Blueprint, request, jsonify
from app import db
from app.models import Document, Category
from app.services.ai import (
    classification_service,
    tagging_service, 
    semantic_service,
    recommendation_service,
    ai_management
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 创建AI功能蓝图
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/api/ai/health', methods=['GET'])
def ai_health_check():
    """AI服务健康检查"""
    try:
        health_status = ai_management.health_check()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"AI健康检查失败: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@ai_bp.route('/api/ai/stats', methods=['GET'])
def ai_service_stats():
    """获取AI服务统计信息"""
    try:
        stats = ai_management.get_service_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取AI统计失败: {e}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/api/ai/initialize', methods=['POST'])
def initialize_ai_services():
    """手动初始化AI服务"""
    try:
        results = ai_management.initialize_all_services()
        return jsonify(results)
    except Exception as e:
        logger.error(f"AI服务初始化失败: {e}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/api/documents/ai', methods=['POST'])
def create_document_with_ai():
    """使用AI辅助创建文档（自动分类和标签）"""
    try:
        data = request.get_json()
        
        # 基础验证
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({'error': '标题和内容不能为空'}), 400
        
        title = data['title']
        content = data['content']
        existing_tags = data.get('tags', [])
        
        # AI自动处理
        ai_results = {}
        
        # 1. 自动分类
        classification_result = classification_service.process(
            content, 
            title=title, 
            content=content
        )
        ai_results['classification'] = classification_result
        
        # 2. 自动标签
        tagging_result = tagging_service.process(
            content,
            title=title,
            content=content,
            existing_tags=existing_tags
        )
        ai_results['tagging'] = tagging_result
        
        # 创建文档
        document = Document(
            title=title,
            content=content,
            file_type=data.get('file_type', 'text'),
            category_id=classification_result.get('category_id'),
            tags=tagging_result.get('tags', existing_tags)
        )
        
        db.session.add(document)
        db.session.commit()
        
        # 刷新推荐服务的数据
        try:
            recommendation_service.refresh()
        except Exception as e:
            logger.warning(f"刷新推荐数据失败: {e}")
        
        return jsonify({
            'message': '文档创建成功（AI辅助）',
            'document': document.to_dict(),
            'ai_processing': ai_results
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"AI辅助创建文档失败: {e}")
        return jsonify({'error': f'创建文档失败: {str(e)}'}), 500

@ai_bp.route('/api/documents/<int:doc_id>/ai-suggest', methods=['GET'])
def get_ai_suggestions(doc_id):
    """获取文档的AI建议（分类和标签）"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        # 获取AI建议
        classification_result = classification_service.process(
            document.content,
            title=document.title,
            content=document.content
        )
        
        tagging_result = tagging_service.process(
            document.content,
            title=document.title,
            content=document.content,
            existing_tags=document.tags or []
        )
        
        # 获取分类详情
        suggested_category = None
        if classification_result.get('category_id'):
            suggested_category = Category.query.get(classification_result['category_id'])
        
        return jsonify({
            'document_id': doc_id,
            'document_title': document.title,
            'suggestions': {
                'category': suggested_category.to_dict() if suggested_category else None,
                'tags': tagging_result.get('tags', []),
                'analysis': {
                    'current_category_id': document.category_id,
                    'suggested_category_id': classification_result.get('category_id'),
                    'current_tags': document.tags or [],
                    'suggested_tags': tagging_result.get('tags', [])
                }
            },
            'confidence': {
                'classification': classification_result.get('confidence', 0),
                'tagging_count': tagging_result.get('tags_count', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"获取AI建议失败: {e}")
        return jsonify({'error': f'获取AI建议失败: {str(e)}'}), 500

@ai_bp.route('/api/documents/<int:doc_id>/ai-apply', methods=['POST'])
def apply_ai_suggestions(doc_id):
    """应用AI建议到文档"""
    try:
        document = Document.query.get_or_404(doc_id)
        data = request.get_json() or {}
        
        # 获取最新AI建议
        classification_result = classification_service.process(
            document.content,
            title=document.title,
            content=document.content
        )
        
        tagging_result = tagging_service.process(
            document.content,
            title=document.title,
            content=document.content,
            existing_tags=document.tags or []
        )
        
        updated = False
        applied_changes = {}
        
        # 应用分类建议
        if data.get('apply_category', False) and classification_result.get('category_id'):
            old_category_id = document.category_id
            document.category_id = classification_result['category_id']
            updated = True
            applied_changes['category'] = {
                'from': old_category_id,
                'to': classification_result['category_id'],
                'confidence': classification_result.get('confidence', 0)
            }
        
        # 应用标签建议
        if data.get('apply_tags', False):
            old_tags = document.tags or []
            document.tags = tagging_result.get('tags', old_tags)
            updated = True
            applied_changes['tags'] = {
                'from': old_tags,
                'to': document.tags,
                'added_count': len(set(document.tags) - set(old_tags))
            }
        
        if updated:
            document.updated_at = datetime.utcnow()
            db.session.commit()
            
            # 刷新推荐数据
            try:
                recommendation_service.refresh()
            except Exception as e:
                logger.warning(f"刷新推荐数据失败: {e}")
        
        return jsonify({
            'message': 'AI建议应用成功',
            'applied_changes': applied_changes,
            'updated': updated,
            'suggestions': {
                'category_id': classification_result.get('category_id'),
                'tags': tagging_result.get('tags', [])
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"应用AI建议失败: {e}")
        return jsonify({'error': f'应用AI建议失败: {str(e)}'}), 500

@ai_bp.route('/api/documents/<int:doc_id>/recommend', methods=['GET'])
def get_document_recommendations(doc_id):
    """获取相似文档推荐"""
    try:
        top_k = request.args.get('top_k', 5, type=int)
        
        recommendation_result = recommendation_service.recommend_similar_documents(
            document_id=doc_id,
            top_k=top_k
        )
        
        return jsonify({
            'document_id': doc_id,
            'recommendations': recommendation_result
        })
        
    except Exception as e:
        logger.error(f"获取文档推荐失败: {e}")
        return jsonify({'error': f'获取推荐失败: {str(e)}'}), 500

@ai_bp.route('/api/ai/recommend/by-content', methods=['POST'])
def recommend_by_content():
    """基于内容推荐文档"""
    try:
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'error': '内容不能为空'}), 400
        
        content = data['content']
        top_k = data.get('top_k', 5)
        
        recommendation_result = recommendation_service.recommend_by_content(
            content=content,
            top_k=top_k
        )
        
        return jsonify({
            'query_content': content[:100] + '...' if len(content) > 100 else content,
            'recommendations': recommendation_result
        })
        
    except Exception as e:
        logger.error(f"基于内容推荐失败: {e}")
        return jsonify({'error': f'推荐失败: {str(e)}'}), 500

@ai_bp.route('/api/ai/semantic/similarity', methods=['POST'])
def calculate_semantic_similarity():
    """计算两个文本的语义相似度"""
    try:
        data = request.get_json()
        if not data or not data.get('text1') or not data.get('text2'):
            return jsonify({'error': '需要提供text1和text2参数'}), 400
        
        text1 = data['text1']
        text2 = data['text2']
        
        similarity_result = semantic_service.semantic_similarity(text1, text2)
        
        return jsonify({
            'text1': text1[:100] + '...' if len(text1) > 100 else text1,
            'text2': text2[:100] + '...' if len(text2) > 100 else text2,
            'similarity': similarity_result
        })
        
    except Exception as e:
        logger.error(f"计算语义相似度失败: {e}")
        return jsonify({'error': f'计算相似度失败: {str(e)}'}), 500

@ai_bp.route('/api/ai/analyze/text', methods=['POST'])
def analyze_text():
    """综合分析文本（分类 + 标签）"""
    try:
        data = request.get_json()
        if not data or not data.get('text'):
            return jsonify({'error': '文本内容不能为空'}), 400
        
        text = data['text']
        title = data.get('title', '')
        
        # 并行处理分类和标签
        classification_result = classification_service.process(
            text, title=title, content=text
        )
        tagging_result = tagging_service.process(
            text, title=title, content=text
        )
        
        return jsonify({
            'analysis': {
                'classification': classification_result,
                'tagging': tagging_result
            },
            'text_preview': text[:200] + '...' if len(text) > 200 else text
        })
        
    except Exception as e:
        logger.error(f"文本分析失败: {e}")
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@ai_bp.route('/api/ai/search/semantic', methods=['POST'])
def semantic_search():
    """语义搜索"""
    try:
        data = request.get_json()
        if not data or not data.get('query'):
            return jsonify({'error': '搜索查询不能为空'}), 400
        
        query = data['query']
        top_k = data.get('top_k', 10)
        
        # 获取候选文档
        documents = Document.query.filter(
            Document.content.isnot(None)
        ).limit(50).all()
        
        # 准备文档数据
        doc_data = []
        for doc in documents:
            doc_data.append({
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,
                'category_id': doc.category_id,
                'tags': doc.tags or []
            })
        
        # 执行语义搜索
        search_result = semantic_service.semantic_search(
            query=query,
            documents=doc_data,
            top_k=top_k
        )
        
        return jsonify({
            'query': query,
            'search_results': search_result,
            'candidate_count': len(doc_data)
        })
        
    except Exception as e:
        logger.error(f"语义搜索失败: {e}")
        return jsonify({'error': f'搜索失败: {str(e)}'}), 500
