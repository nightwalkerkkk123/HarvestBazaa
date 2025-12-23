#!/usr/bin/env python
"""
测试购物车页面布局修复
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from market.models import Specialty, Origin, ShoppingCart

User = get_user_model()

def test_cart_layout():
    """测试购物车页面布局"""
    print("=" * 50)
    print("测试购物车页面布局修复")
    print("=" * 50)
    
    # 创建测试客户端
    client = Client()
    client.defaults['HTTP_HOST'] = '127.0.0.1'
    
    try:
        # 1. 创建测试用户
        print("\n1. 创建测试用户...")
        
        user, created = User.objects.get_or_create(
            username='testuser_layout',
            defaults={
                'password': 'testpass123',
                'email': 'test@example.com',
                'status': '正常'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"创建用户: {user.username}")
        else:
            print(f"使用已存在的用户: {user.username}")
        
        # 2. 创建测试产品
        print("\n2. 创建测试产品...")
        
        # 创建测试产地
        origin, created = Origin.objects.get_or_create(
            province='测试省',
            city='测试市',
            district='测试区',
            defaults={'origin_name': '测试产地'}
        )
        print(f"{'创建' if created else '使用已存在的'}测试产地: {origin.origin_name}")
        
        # 创建测试产品
        product, created = Specialty.objects.get_or_create(
            name='测试布局产品',
            defaults={
                'origin': origin,
                'category': '测试类别',
                'description': '这是一个用于测试布局的产品',
                'price': 88.88,
                'sale_start_time': '2023-01-01',
                'sale_end_time': '2023-12-31',
                'status': '上架',
                'publisher': user
            }
        )
        print(f"{'创建' if created else '使用已存在的'}测试产品: {product.name}")
        
        # 3. 创建购物车记录（数量为3）
        print("\n3. 创建购物车记录...")
        
        # 删除可能存在的旧记录
        ShoppingCart.objects.filter(user=user, specialty=product).delete()
        
        # 创建新的购物车记录
        cart_item = ShoppingCart.objects.create(
            user=user,
            specialty=product,
            quantity=3
        )
        print(f"创建购物车记录: {product.name} x {cart_item.quantity}")
        
        # 4. 登录用户并访问购物车页面
        print("\n4. 访问购物车页面...")
        
        # 登录用户
        login_result = client.login(username='testuser_layout', password='testpass123')
        print(f"用户登录结果: {'成功' if login_result else '失败'}")
        
        if login_result:
            # 访问购物车页面
            response = client.get('/cart/')
            print(f"访问购物车页面状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ 成功访问购物车页面")
                
                # 检查页面内容
                content = response.content.decode('utf-8')
                
                # 检查是否有产品名称
                if product.name in content:
                    print(f"✓ 找到产品: {product.name}")
                else:
                    print(f"✗ 未找到产品: {product.name}")
                
                # 检查单价显示
                if f"¥{product.price}" in content:
                    print(f"✓ 正确显示单价: ¥{product.price}")
                else:
                    print(f"✗ 单价显示不正确")
                
                # 检查数量显示
                if f"{cart_item.quantity}" in content:
                    print(f"✓ 正确显示数量: {cart_item.quantity}")
                else:
                    print(f"✗ 数量显示不正确")
                
                # 计算预期的小计金额
                expected_subtotal = product.price * cart_item.quantity
                expected_subtotal_str = f"¥{expected_subtotal:.2f}"
                
                # 检查小计金额显示
                if expected_subtotal_str in content:
                    print(f"✓ 正确显示小计金额: {expected_subtotal_str}")
                else:
                    print(f"✗ 小计金额显示不正确，预期: {expected_subtotal_str}")
                    
                    # 查找实际的小计金额
                    import re
                    subtotal_pattern = r'¥(\d+\.\d{2})'
                    matches = re.findall(subtotal_pattern, content)
                    if matches:
                        print(f"实际找到的小计金额: ¥{matches[-1]}")
                    else:
                        print("未找到任何小计金额")
                
                # 检查总金额显示
                if expected_subtotal_str in content and content.count(expected_subtotal_str) >= 2:
                    print(f"✓ 正确显示总金额: {expected_subtotal_str}")
                else:
                    print(f"✗ 总金额显示不正确，预期: {expected_subtotal_str}")
                
                # 检查是否使用了mul过滤器
                if 'mul:' in content:
                    print("✓ 页面使用了mul过滤器")
                else:
                    print("✗ 页面未使用mul过滤器")
                
            else:
                print("✗ 访问购物车页面失败")
        else:
            print("✗ 用户登录失败")
        
        print("\n" + "=" * 50)
        print("购物车页面布局测试完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_cart_layout()