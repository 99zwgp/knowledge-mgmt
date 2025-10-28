#!/bin/bash

echo "=== 搜索功能完整测试 ==="

# 测试1: OR模式搜索 Python 编程 (应该返回2个结果)
echo -e "\n1. OR模式: Python 编程"
curl -s -G "http://localhost:5000/api/search/advanced" \
  --data-urlencode "q=Python 编程" \
  --data-urlencode "search_mode=or" | python3 -m json.tool

# 测试2: AND模式搜索 Python 编程 (应该返回1个结果)
echo -e "\n2. AND模式: Python 编程"
curl -s -G "http://localhost:5000/api/search/advanced" \
  --data-urlencode "q=Python 编程" \
  --data-urlencode "search_mode=and" | python3 -m json.tool

# 测试3: OR模式搜索 机器学习 Python (应该返回2个结果)
echo -e "\n3. OR模式: 机器学习 Python"
curl -s -G "http://localhost:5000/api/search/advanced" \
  --data-urlencode "q=机器学习 Python" \
  --data-urlencode "search_mode=or" | python3 -m json.tool

# 测试4: AND模式搜索 机器学习 Python (应该返回1个结果)
echo -e "\n4. AND模式: 机器学习 Python"
curl -s -G "http://localhost:5000/api/search/advanced" \
  --data-urlencode "q=机器学习 Python" \
  --data-urlencode "search_mode=and" | python3 -m json.tool

echo -e "\n=== 测试完成 ==="
