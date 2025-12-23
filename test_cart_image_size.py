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
from market.models import Specialty, ShoppingCart, Origin
from decimal import Decimal

# 创建测试客户端
client = Client()

# 创建测试用户
User = get_user_model()

# 检查用户是否已存在，如果存在则删除
try:
    existing_user = User.objects.get(username='test_img_user')
    existing_user.delete()
    print("删除已存在的测试用户")
except User.DoesNotExist:
    pass

user = User.objects.create_user(username='test_img_user', password='testpass123')

# 创建测试产品
origin = Origin.objects.create(province='江苏省', city='苏州市')
product = Specialty.objects.create(
    name='测试图片大小产品',
    price=Decimal('99.99'),
    origin=origin,
    description='用于测试图片大小的产品',
    image='product_images/六只装精选母蟹.png',  # 使用实际存在的图片
    publisher=user  # 添加发布者
)

# 创建购物车项
cart_item = ShoppingCart.objects.create(
    user=user,
    specialty=product,
    quantity=2
)

# 登录用户
client.login(username='test_img_user', password='testpass123')

# 访问购物车页面
response = client.get('/cart/')
print(f"购物车页面状态码: {response.status_code}")

# 检查响应内容
content = response.content.decode('utf-8')

# 查找图片元素
import re

# 查找所有图片元素
img_pattern = r'<img[^>]*>'
imgs = re.findall(img_pattern, content)

print(f"\n找到 {len(imgs)} 个图片元素:")
print("-" * 50)

for i, img in enumerate(imgs):
    print(f"图片 {i+1}:")
    print(img)
    
    # 检查是否有src属性
    src_match = re.search(r'src="([^"]*)"', img)
    if src_match:
        print(f"  源文件: {src_match.group(1)}")
    
    # 检查是否有alt属性
    alt_match = re.search(r'alt="([^"]*)"', img)
    if alt_match:
        print(f"  替代文本: {alt_match.group(1)}")
    
    print()

# 检查是否有cart-product-image类
if 'cart-product-image' in content:
    print("✓ 找到cart-product-image类")
else:
    print("✗ 未找到cart-product-image类")

# 检查CSS是否正确加载
if 'cart.css' in content:
    print("✓ CSS文件已加载")
else:
    print("✗ CSS文件未加载")

# 检查产品名称是否正确显示
if product.name in content:
    print(f"✓ 产品名称正确显示: {product.name}")
else:
    print(f"✗ 产品名称未显示: {product.name}")

# 清理测试数据
cart_item.delete()
product.delete()
origin.delete()
user.delete()

print("\n测试完成!")