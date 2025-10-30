#!/bin/bash

echo "=== AI功能测试 ==="

# 测试1: AI辅助创建文档
echo -e "\n1. 测试AI辅助创建文档（技术类）"
curl -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python异步编程详解",
    "content": "Python的asyncio库提供了强大的异步编程能力，可以显著提升IO密集型应用的性能。本文详细介绍了async/await语法、事件循环和协程的使用方法。",
    "tags": ["Python"]
  }'

echo -e "\n\n2. 测试AI辅助创建文档（学习类）"
curl -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "机器学习学习心得",
    "content": "在学习机器学习的过程中，我总结了以下几点心得体会：理解数学基础很重要，多动手实践，参加Kaggle比赛提升实战能力。",
    "tags": ["学习"]
  }'

echo -e "\n\n3. 测试AI建议功能"
# 先获取一个文档ID，然后测试AI建议
DOC_ID=10  # 使用已有的文档ID
curl http://localhost:5000/api/documents/$DOC_ID/ai-suggest

echo -e "\n\n4. 测试应用AI建议"
curl -X POST http://localhost:5000/api/documents/$DOC_ID/ai-apply \
  -H "Content-Type: application/json" \
  -d '{
    "apply_category": true,
    "apply_tags": true
  }'

echo -e "\n\n=== AI功能测试完成 ==="
