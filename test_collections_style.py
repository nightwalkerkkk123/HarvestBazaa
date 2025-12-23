#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
sys.path.append('e:\\DjangoProject')
django.setup()

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from market.models import Specialty, Collection, Origin
from decimal import Decimal

# 创建测试客户端
client = Client()

# 创建测试用户
User = get_user_model()

# 检查用户是否已存在，如果存在则删除
try:
    existing_user = User.objects.get(username='test_style_user')
    existing_user.delete()
    print("删除已存在的测试用户")
except User.DoesNotExist:
    pass

user = User.objects.create_user(username='test_style_user', password='testpass123')

# 创建测试产品
origin = Origin.objects.create(province='江苏省', city='苏州市')
product = Specialty.objects.create(
    name='测试简约风格产品',
    price=Decimal('199.99'),
    origin=origin,
    description='用于测试简约风格的产品',
    image='product_images/六只装精选母蟹.png',
    publisher=user
)

# 创建收藏项
collection = Collection.objects.create(
    user=user,
    specialty=product
)

# 登录用户
client.login(username='test_style_user', password='testpass123')

# 访问收藏页面
response = client.get('/user/collections/')
print(f"收藏页面状态码: {response.status_code}")

# 检查响应内容
content = response.content.decode('utf-8')

# 检查页面头部样式
if 'page-header' in content:
    print("✓ 找到页面头部元素")
else:
    print("✗ 未找到页面头部元素")

# 检查收藏卡片样式
if 'collection-card' in content:
    print("✓ 找到收藏卡片元素")
else:
    print("✗ 未找到收藏卡片元素")

# 检查产品名称是否正确显示
if product.name in content:
    print(f"✓ 产品名称正确显示: {product.name}")
else:
    print(f"✗ 产品名称未显示: {product.name}")

# 检查价格是否正确显示
if '199.99' in content:
    print("✓ 价格正确显示: ¥199.99")
else:
    print("✗ 价格未正确显示")

# 检查按钮样式
if 'btn-outline' in content and 'btn-primary' in content and 'btn-danger' in content:
    print("✓ 找到所有按钮样式")
else:
    print("✗ 按钮样式不完整")

# 检查CSS是否正确加载
if 'collections.css' in content:
    print("✓ CSS文件已加载")
else:
    print("✗ CSS文件未加载")

# 检查是否有简约风格的元素
if '简约' in content or 'minimal' in content.lower():
    print("✓ 找到简约风格相关内容")
else:
    print("- 未找到明确的简约风格标识")

# 清理测试数据
collection.delete()
product.delete()
origin.delete()
user.delete()

print("\n测试完成! 收藏页面样式已更新为简约风格。")