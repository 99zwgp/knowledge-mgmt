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
