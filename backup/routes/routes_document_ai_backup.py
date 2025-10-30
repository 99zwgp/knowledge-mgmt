@main_bp.route('/api/documents/ai', methods=['POST'])
def create_document_with_ai():
    """使用AI辅助创建文档（自动分类和标签）"""
    try:
        data = request.get_json()
        
        # 基础验证
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({'error': '标题和内容不能为空'}), 400
        
        # AI自动处理
        from app.services.ai.classification_service import classification_service
        from app.services.ai.tagging_service import tagging_service
        
        title = data['title']
        content = data['content']
        existing_tags = data.get('tags', [])
        
        # 1. 自动分类
        category_result = classification_service.process(
            content, 
            title=title, 
            content=content
        )
        
        # 2. 自动标签
        tagging_result = tagging_service.process(
            content,
            title=title,
            content=content,
            existing_tags=existing_tags
        )
        
        # 创建文档
        document = Document(
            title=title,
            content=content,
            file_type=data.get('file_type', 'text'),
            category_id=category_result.get('category_id'),
            tags=tagging_result.get('tags', existing_tags)
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'message': '文档创建成功（AI辅助）',
            'document': document.to_dict(),
            'ai_processing': {
                'auto_category': category_result,
                'auto_tags': tagging_result
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建文档失败: {str(e)}'}), 500

@main_bp.route('/api/documents/<int:doc_id>/ai-suggest', methods=['GET'])
def get_ai_suggestions(doc_id):
    """获取文档的AI建议（分类和标签）"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        from app.services.ai.classification_service import classification_service
        from app.services.ai.tagging_service import tagging_service
        
        # 获取AI建议
        category_result = classification_service.process(
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
        if category_result['category_id']:
            suggested_category = Category.query.get(category_result['category_id'])
        
        return jsonify({
            'document_id': doc_id,
            'suggestions': {
                'category': suggested_category.to_dict() if suggested_category else None,
                'tags': tagging_result['tags'],
                'analysis': {
                    'current_category_id': document.category_id,
                    'suggested_category_id': category_result['category_id'],
                    'current_tags': document.tags or [],
                    'suggested_tags': tagging_result['tags']
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'获取AI建议失败: {str(e)}'}), 500

@main_bp.route('/api/documents/<int:doc_id>/ai-apply', methods=['POST'])
def apply_ai_suggestions(doc_id):
    """应用AI建议到文档"""
    try:
        document = Document.query.get_or_404(doc_id)
        data = request.get_json() or {}
        
        from app.services.ai.classification_service import classification_service
        from app.services.ai.tagging_service import tagging_service
        
        # 获取最新AI建议
        category_result = classification_service.process(
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
        
        # 应用分类建议（如果用户确认或强制应用）
        if data.get('apply_category', False) and category_result['category_id']:
            document.category_id = category_result['category_id']
            updated = True
        
        # 应用标签建议
        if data.get('apply_tags', False):
            document.tags = tagging_result['tags']
            updated = True
        
        if updated:
            document.updated_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'message': 'AI建议应用成功',
            'applied': {
                'category': data.get('apply_category', False),
                'tags': data.get('apply_tags', False)
            },
            'suggestions': {
                'category_id': category_result['category_id'],
                'tags': tagging_result['tags']
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'应用AI建议失败: {str(e)}'}), 500
