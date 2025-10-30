#!/bin/bash

echo "=== 部署验证脚本 ==="

# 检查依赖
echo -e "\n1. 检查Python依赖"
pip list | grep -E "(Flask|jieba|scikit|numpy)"

# 检查服务状态
echo -e "\n2. 检查API服务状态"
curl -s http://localhost:5000/ | python3 -m json.tool

# 检查AI服务状态
echo -e "\n3. 检查AI服务状态"
curl -s http://localhost:5000/api/ai/health | python3 -m json.tool

# 检查数据库连接
echo -e "\n4. 检查数据库连接"
python3 -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        result = db.session.execute('SELECT 1')
        print('✅ 数据库连接正常')
    except Exception as e:
        print('❌ 数据库连接失败:', e)
"

# 检查AI服务初始化
echo -e "\n5. 检查AI服务初始化"
python3 -c "
from app.services.ai import ai_management
stats = ai_management.get_service_stats()
print('AI服务统计:')
for name, stat in stats['stats'].items():
    status = '✅' if stat['initialized'] else '❌'
    print(f'  {status} {name}: {stat[\\\"service_name\\\"]}')
"

echo -e "\n=== 部署验证完成 ==="
