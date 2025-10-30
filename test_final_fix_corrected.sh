#!/bin/bash

echo "=== 最终修复验证 ==="

echo -e "\n1. 测试基于内容的推荐（修复后）"
curl -s -X POST http://localhost:5000/api/ai/recommend/by-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "我想学习Web开发，特别是前端框架Vue.js和后端Flask框架的集成",
    "top_k": 2
  }' | python3 -c "
import sys, json
try:
    result = json.load(sys.stdin)
    if 'recommendations' in result:
        recs = result['recommendations']
        print('✅ 推荐成功！')
        count = len(recs)
        print('找到', count, '个推荐文档:')
        for rec in recs:
            title = rec.get('title', '未知标题')
            similarity = rec.get('similarity', 0)
            print('   📄', title, '(相似度:', similarity, ')')
    else:
        error_msg = result.get('error', '未知错误')
        print('❌ 推荐失败:', error_msg)
except Exception as e:
    print('❌ 解析错误:', e)
"

echo -e "\n2. 测试文档推荐"
curl -s "http://localhost:5000/api/documents/16/recommend?top_k=2" | python3 -c "
import sys, json
try:
    result = json.load(sys.stdin)
    recs = result['recommendations']
    if recs.get('success'):
        print('✅ 文档推荐成功！')
        count = recs.get('count', 0)
        print('找到', count, '个相关文档')
        for doc in recs.get('recommendations', [])[:2]:
            title = doc.get('title', '未知标题')
            similarity = doc.get('similarity', 0)
            print('   📄', title, '(相似度:', similarity, ')')
    else:
        method = recs.get('method', '未知方法')
        print('⚠️ 使用降级推荐:', method)
        for doc in recs.get('recommendations', [])[:2]:
            title = doc.get('title', '未知标题')
            print('   📄', title)
except Exception as e:
    print('❌ 解析错误:', e)
"

echo -e "\n3. 测试搜索功能（OR模式）"
curl -s "http://localhost:5000/api/search/advanced?q=Python+编程&search_mode=or" | python3 -c "
import sys, json
result = json.load(sys.stdin)
total = result['pagination']['total']
print('搜索找到', total, '个结果')
for doc in result['results'][:3]:
    title = doc['title']
    score = doc['relevance_score']
    print('   📄', title, '(相关度:', score, ')')
"

echo -e "\n4. 测试AI服务健康状态"
curl -s http://localhost:5000/api/ai/health | python3 -c "
import sys, json
result = json.load(sys.stdin)
print('AI服务状态:', result['overall_status'])
for service, status in result['services'].items():
    state = '🟢' if status['initialized'] else '🔴'
    service_status = status.get('status', 'unknown')
    print('   ', state, service + ':', service_status)
"

echo -e "\n5. 测试AI辅助创建文档"
curl -s -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "最终测试文档 - 项目完成验证",
    "content": "这是用于验证项目最终完成的测试文档，测试AI分类和标签生成功能。",
    "tags": ["测试"]
  }' | python3 -c "
import sys, json
result = json.load(sys.stdin)
if 'document' in result:
    doc = result['document']
    title = doc.get('title', '未知标题')
    category = doc.get('category', {}).get('name', '未分类')
    tags = doc.get('tags', [])
    print('✅ AI文档创建成功！')
    print('   标题:', title)
    print('   分类:', category)
    print('   标签:', ', '.join(tags[:5]))
else:
    print('❌ 创建失败')
"

echo -e "\n=== 验证完成 ==="
