#!/bin/bash

echo "🚀 启动带看板的AI知识管理系统"

# 备份原应用文件
cp app/__init__.py app/__init__.backup.py 2>/dev/null || echo "无备份文件"

# 更新应用文件
cp app/__init__with_dashboard.py app/__init__.py

# 确保模板目录存在
mkdir -p app/templates

echo "✅ 看板系统配置完成"
echo ""
echo "🎯 功能清单:"
echo "   • 📊 系统状态监控"
echo "   • 📝 文档创建和AI处理"
echo "   • 🤖 AI分类测试"
echo "   • 📚 文档列表展示"
echo ""
echo "🚀 启动系统:"
echo "   python run.py"
echo ""
echo "🌐 访问地址: http://localhost:5000"
