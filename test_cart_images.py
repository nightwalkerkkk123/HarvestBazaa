#!/usr/bin/env python
"""
测试购物车页面图片显示
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

def test_shopping_cart_images():
    """测试购物车页面的图片显示"""
    print("=" * 50)
    print("测试购物车页面图片显示")
    print("=" * 50)
    
    # 创建测试客户端
    client = Client()
    client.defaults['HTTP_HOST'] = '127.0.0.1'
    
    try:
        # 1. 创建测试用户
        print("\n1. 创建测试用户...")
        
        user, created = User.objects.get_or_create(
            username='testuser_cart',
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
        
        # 2. 创建测试产品（有图片和没有图片的）
        print("\n2. 创建测试产品...")
        
        # 创建测试产地
        origin, created = Origin.objects.get_or_create(
            province='测试省',
            city='测试市',
            district='测试区',
            defaults={'origin_name': '测试产地'}
        )
        print(f"{'创建' if created else '使用已存在的'}测试产地: {origin.origin_name}")
        
        # 创建有图片的产品
        product_with_image, created = Specialty.objects.get_or_create(
            name='哈密甜瓜',
            defaults={
                'origin': origin,
                'category': '水果',
                'description': '新疆哈密甜瓜',
                'price': 29.99,
                'sale_start_time': '2023-01-01',
                'sale_end_time': '2023-12-31',
                'status': '上架',
                'publisher': user,
                'image': 'product_images/哈密甜瓜.png'
            }
        )
        print(f"{'创建' if created else '使用已存在的'}有图片的产品: {product_with_image.name}")
        
        # 创建没有图片的产品
        product_without_image, created = Specialty.objects.get_or_create(
            name='测试无图产品2',
            defaults={
                'origin': origin,
                'category': '测试类别',
                'description': '这是一个没有图片的测试产品2',
                'price': 38.88,
                'sale_start_time': '2023-01-01',
                'sale_end_time': '2023-12-31',
                'status': '上架',
                'publisher': user
            }
        )
        print(f"{'创建' if created else '使用已存在的'}无图片的产品: {product_without_image.name}")
        
        # 3. 创建购物车记录
        print("\n3. 创建购物车记录...")
        
        # 添加有图片的产品到购物车
        cart_with_image, created = ShoppingCart.objects.get_or_create(
            user=user,
            specialty=product_with_image,
            defaults={'quantity': 2}
        )
        print(f"{'创建' if created else '使用已存在的'}有图片产品的购物车记录")
        
        # 添加没有图片的产品到购物车
        cart_without_image, created = ShoppingCart.objects.get_or_create(
            user=user,
            specialty=product_without_image,
            defaults={'quantity': 1}
        )
        print(f"{'创建' if created else '使用已存在的'}无图片产品的购物车记录")
        
        # 4. 登录用户并访问购物车页面
        print("\n4. 访问购物车页面...")
        
        # 登录用户
        login_result = client.login(username='testuser_cart', password='testpass123')
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
                if product_with_image.name in content:
                    print(f"✓ 找到有图片产品: {product_with_image.name}")
                else:
                    print(f"✗ 未找到有图片产品: {product_with_image.name}")
                
                if product_without_image.name in content:
                    print(f"✓ 找到无图片产品: {product_without_image.name}")
                else:
                    print(f"✗ 未找到无图片产品: {product_without_image.name}")
                
                # 检查是否有图片路径
                if 'product_images' in content or 'default-product.svg' in content:
                    print("✓ 页面包含图片路径")
                else:
                    print("✗ 页面不包含图片路径")
                
                # 检查是否使用了product_image过滤器
                if 'product_image' in content:
                    print("✓ 页面使用了product_image过滤器")
                else:
                    print("✗ 页面未使用product_image过滤器")
                
                # 检查图片显示逻辑
                if 'src="' in content:
                    print("✓ 页面包含图片src属性")
                    
                    # 提取所有图片src
                    import re
                    img_srcs = re.findall(r'src="([^"]*)"', content)
                    print(f"找到 {len(img_srcs)} 个图片路径:")
                    for src in img_srcs:
                        print(f"  - {src}")
                else:
                    print("✗ 页面不包含图片src属性")
                
            else:
                print("✗ 访问购物车页面失败")
        else:
            print("✗ 用户登录失败")
        
        print("\n" + "=" * 50)
        print("购物车页面图片显示测试完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_shopping_cart_images()