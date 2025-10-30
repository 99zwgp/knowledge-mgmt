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
        print(f'找到 {len(recs)} 个推荐文档:')
        for rec in recs:
            print(f'   📄 {rec[\\\"title\\\"]} (相似度: {rec[\\\"similarity\\\"]})')
    else:
        print('❌ 推荐失败:', result.get('error', '未知错误'))
except Exception as e:
    print('❌ 解析错误:', e)
"

echo -e "\n2. 测试文档推荐"
curl -s "http://localhost:5000/api/documents/16/recommend?top_k=2" | python3 -c "
import sys, json
try:
    result = json.load(sys.stdin)
    recs = result['recommendations']
    if recs['success']:
        print('✅ 文档推荐成功！')
        print(f'找到 {recs[\\\"count\\\"]} 个相关文档')
        for doc in recs['recommendations'][:2]:
            print(f'   📄 {doc[\\\"title\\\"]} (相似度: {doc[\\\"similarity\\\"]})')
    else:
        print('⚠️ 使用降级推荐:', recs.get('method', '未知方法'))
        for doc in recs.get('recommendations', [])[:2]:
            print(f'   📄 {doc[\\\"title\\\"]}')
except Exception as e:
    print('❌ 解析错误:', e)
"

echo -e "\n3. 测试搜索功能（OR模式）"
curl -s "http://localhost:5000/api/search/advanced?q=Python+编程&search_mode=or" | python3 -c "
import sys, json
result = json.load(sys.stdin)
total = result['pagination']['total']
print(f'搜索找到 {total} 个结果')
for doc in result['results'][:3]:
    title = doc['title']
    score = doc['relevance_score']
    print(f'   📄 {title} (相关度: {score})')
"

echo -e "\n4. 测试AI服务健康状态"
curl -s http://localhost:5000/api/ai/health | python3 -c "
import sys, json
result = json.load(sys.stdin)
print('AI服务状态:', result['overall_status'])
for service, status in result['services'].items():
    state = '🟢' if status['initialized'] else '🔴'
    print(f'   {state} {service}: {status[\\\"status\\\"]}')
"

echo -e "\n=== 验证完成 ==="
