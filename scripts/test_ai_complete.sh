#!/bin/bash

echo "=== 知识管理系统AI功能完整测试 ==="
echo "测试时间: $(date)"

# 等待应用启动
echo -e "\n等待应用启动..."
sleep 3

# 1. 测试AI服务健康状态
echo -e "\n1. 测试AI服务健康状态"
curl -s http://localhost:5000/api/ai/health | python3 -m json.tool

# 2. 测试AI服务统计
echo -e "\n2. 测试AI服务统计"
curl -s http://localhost:5000/api/ai/stats | python3 -m json.tool

# 3. 测试AI辅助创建文档
echo -e "\n3. 测试AI辅助创建文档"

echo -e "\n3.1 技术类文档"
curl -s -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Flask Web开发实战",
    "content": "Flask是一个轻量级的Python Web框架，适合快速开发RESTful API。本文介绍Flask的路由、模板、数据库集成和部署实践。通过学习可以掌握构建现代Web应用的能力。",
    "tags": ["Web开发"]
  }' | python3 -m json.tool

echo -e "\n3.2 学习类文档"  
curl -s -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "机器学习入门学习心得总结",
    "content": "在学习机器学习的过程中，我发现理解数学基础非常重要。线性代数、概率论和微积分是理解算法原理的关键。通过参加Kaggle比赛，我提升了数据预处理和模型调优的实战能力。",
    "tags": ["学习笔记"]
  }' | python3 -m json.tool

echo -e "\n3.3 工作类文档"
curl -s -X POST http://localhost:5000/api/documents/ai \
  -H "Content-Type: application/json" \
  -d '{
    "title": "敏捷开发项目管理经验分享",
    "content": "在最近的项目中，我们采用敏捷开发方法，通过每日站会保持团队沟通，通过迭代评审收集反馈，通过回顾会议持续改进。这种方法显著提升了项目交付质量和团队协作效率。",
    "tags": ["项目管理"]
  }' | python3 -m json.tool

# 4. 测试AI建议功能
echo -e "\n4. 测试AI建议功能"
DOC_ID=$(curl -s http://localhost:5000/api/documents | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['documents'][0]['id'] if data['documents'] else '1')")
echo "使用文档ID: $DOC_ID"

curl -s http://localhost:5000/api/documents/$DOC_ID/ai-suggest | python3 -m json.tool

# 5. 测试文档推荐
echo -e "\n5. 测试文档推荐功能"
curl -s http://localhost:5000/api/documents/$DOC_ID/recommend?top_k=3 | python3 -m json.tool

# 6. 测试语义相似度
echo -e "\n6. 测试语义相似度计算"
curl -s -X POST http://localhost:5000/api/ai/semantic/similarity \
  -H "Content-Type: application/json" \
  -d '{
    "text1": "Python编程语言学习",
    "text2": "学习Python语言编程"
  }' | python3 -m json.tool

# 7. 测试文本分析
echo -e "\n7. 测试文本分析功能"
curl -s -X POST http://localhost:5000/api/ai/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Docker容器技术介绍",
    "text": "Docker是一种容器化技术，可以将应用及其依赖打包成轻量级、可移植的容器。容器可以在任何环境中运行，确保了应用环境的一致性。"
  }' | python3 -m json.tool

# 8. 测试基于内容的推荐
echo -e "\n8. 测试基于内容的推荐"
curl -s -X POST http://localhost:5000/api/ai/recommend/by-content \
  -H "Content-Type: application/json" \
  -d '{
    "content": "我想学习Python Web开发，特别是Flask框架的使用",
    "top_k": 3
  }' | python3 -m json.tool

echo -e "\n=== AI功能测试完成 ==="
echo "测试时间: $(date)"
