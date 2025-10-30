#!/bin/bash

echo "=== 知识管理系统 - 完整功能测试 ==="
echo "测试时间: $(date)"

# 等待应用启动
sleep 2

echo -e "\n1. 📊 系统状态检查"
curl -s http://localhost:5000/api/status | python3 -m json.tool

echo -e "\n2. 🤖 AI服务健康检查"
curl -s http://localhost:5000/api/ai/health | python3 -m json.tool

echo -e "\n3. 🏷️ 测试AI辅助文档创建"
echo -e "\n3.1 技术类文档"
curl -s -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python异步编程与Asyncio详解",
    "content": "Asyncio是Python的异步IO框架，提供了基于协程的并发编程能力。通过async/await语法，可以编写高效的异步代码，特别适合网络请求、文件IO等高延迟操作。本文详细介绍事件循环、任务调度和协程的最佳实践。",
    "tags": ["Python"]
  }' | python3 -m json.tool

echo -e "\n3.2 学习类文档"
curl -s -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "深度学习神经网络学习总结",
    "content": "在学习深度学习的过程中，我重点掌握了卷积神经网络CNN和循环神经网络RNN的原理。通过实践项目，理解了梯度下降、反向传播等优化算法，并在图像分类和自然语言处理任务中取得了良好效果。",
    "tags": ["学习笔记"]
  }' | python3 -m json.tool

echo -e "\n4. 🔍 测试AI建议功能"
DOC_ID=$(curl -s http://localhost:5000/api/documents | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['documents'][0]['id'] if data['documents'] else '1')")
echo "测试文档ID: $DOC_ID"
curl -s http://localhost:5000/api/documents/$DOC_ID/ai-suggest | python3 -m json.tool

echo -e "\n5. 💡 测试文档推荐"
curl -s "http://localhost:5000/api/documents/$DOC_ID/recommend?top_k=3" | python3 -m json.tool

echo -e "\n6. 📈 测试语义分析"
curl -s -X POST http://localhost:5000/api/ai/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "title": "微服务架构设计与实践",
    "text": "微服务架构将单体应用拆分为多个小型服务，每个服务独立部署和扩展。这种架构提高了系统的可维护性和可扩展性，但同时也带来了分布式系统的复杂性，如服务发现、配置管理和分布式事务等挑战。"
  }' | python3 -m json.tool

echo -e "\n7. 🔗 测试语义相似度"
curl -s -X POST http://localhost:5000/api/ai/semantic/similarity \
  -H "Content-Type: application/json" \
  -d '{
    "text1": "机器学习深度学习人工智能",
    "text2": "人工智能机器学习深度学习"
  }' | python3 -m json.tool

echo -e "\n8. 🎯 测试基于内容的推荐"
curl -s -X POST http://localhost:5000/api/ai/recommend/by-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "我想学习Web开发，特别是前端框架Vue.js和后端Flask框架的集成",
    "top_k": 3
  }' | python3 -m json.tool

echo -e "\n9. 📚 测试搜索功能"
curl -s "http://localhost:5000/api/search/advanced?q=Python+编程&search_mode=and" | python3 -m json.tool

echo -e "\n10. 📈 系统统计"
curl -s http://localhost:5000/api/search/stats | python3 -m json.tool

echo -e "\n=== 🎉 完整功能测试完成 ==="
echo "测试时间: $(date)"
