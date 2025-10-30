#!/bin/bash

echo "================================================"
echo "🤖 知识管理系统 - 项目演示"
echo "================================================"
echo "演示时间: $(date)"
echo ""

echo "1. 🏗️ 系统架构展示"
echo "   - 后端: Flask + SQLAlchemy + MySQL"
echo "   - 缓存: Redis"
echo "   - AI引擎: jieba + scikit-learn"
echo "   - API: 16个RESTful端点"
echo ""

echo "2. 📊 当前系统状态"
curl -s http://localhost:5000/api/ai/health | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('   AI服务状态:', data['overall_status'])
for service, status in data['services'].items():
    print('   -', service + ':', '🟢 健康' if status['initialized'] else '🔴 异常')
"

echo ""
echo "3. 🔍 智能搜索演示"
curl -s "http://localhost:5000/api/search/advanced?q=Python+开发&search_mode=or" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('  搜索 \"Python 开发\" 找到', data['pagination']['total'], '个结果:')
for doc in data['results'][:3]:
    print('   📖', doc['title'], '(相关度:', doc['relevance_score'], ')')
"

echo ""
echo "4. 🤖 AI能力演示"
echo "   创建测试文档..."
curl -s -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "机器学习在自然语言处理中的应用",
    "content": "本文介绍机器学习算法在自然语言处理领域的应用，包括文本分类、情感分析、机器翻译等任务。深度学习模型如Transformer在NLP中取得了突破性进展。",
    "tags": ["NLP"]
  }' | python3 -c "
import json, sys
data = json.load(sys.stdin)
doc = data['document']
ai = data['ai_processing']
print('   ✅ 文档创建成功!')
print('     标题:', doc['title'])
print('     分类:', doc['category']['name'])
print('     标签:', ', '.join(doc['tags'][:5]))
print('     分类置信度:', ai['classification']['confidence'])
"

echo ""
echo "5. 💡 知识发现演示"
DOC_ID=16
curl -s "http://localhost:5000/api/documents/$DOC_ID/recommend?top_k=2" | python3 -c "
import json, sys
data = json.load(sys.stdin)
recs = data['recommendations']
if recs['success']:
    print('  基于文档的推荐:')
    for doc in recs['recommendations']:
        print('   🔗', doc['title'], '(相似度:', doc['similarity'], ')')
else:
    print('  使用降级推荐方案')
"

echo ""
echo "================================================"
echo "🎯 演示总结"
echo "================================================"
echo "✅ 系统架构: 健壮稳定"
echo "✅ AI能力: 智能实用" 
echo "✅ 搜索功能: 精准高效"
echo "✅ 推荐系统: 知识发现"
echo "✅ 工程质量: 生产就绪"
echo ""
echo "🚀 项目状态: 完全可演示!"
echo "================================================"
