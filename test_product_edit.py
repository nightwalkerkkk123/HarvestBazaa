#!/usr/bin/env python
"""
产品编辑功能测试脚本
测试用户和管理员编辑产品的功能
"""

import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from market.models import Specialty, Origin

User = get_user_model()

def test_product_edit():
    """测试产品编辑功能"""
    print("=" * 50)
    print("产品编辑功能测试")
    print("=" * 50)
    
    # 创建测试客户端
    from django.test.utils import setup_test_environment
    from django.test.client import Client
    
    # 设置测试环境
    setup_test_environment()
    client = Client()
    
    # 设置测试客户端的HTTP_HOST
    client.defaults['HTTP_HOST'] = '127.0.0.1'
    
    try:
        # 1. 创建测试用户（普通用户和管理员）
        print("\n1. 创建测试用户...")
        
        # 普通用户
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'password': 'testpass123',
                'email': 'test@example.com',
                'status': '正常'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"创建普通用户: {user.username}")
        else:
            print(f"使用已存在的普通用户: {user.username}")
        
        # 管理员用户
        admin, created = User.objects.get_or_create(
            username='testadmin',
            defaults={
                'password': 'adminpass123',
                'email': 'admin@example.com',
                'role': '管理员',
                'status': '正常'
            }
        )
        if created:
            admin.set_password('adminpass123')
            admin.save()
            print(f"创建管理员用户: {admin.username}")
        else:
            print(f"使用已存在的管理员用户: {admin.username}")
        
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
        specialty, created = Specialty.objects.get_or_create(
            name='测试产品',
            defaults={
                'origin': origin,
                'category': '测试类别',
                'description': '这是一个测试产品',
                'price': 99.99,
                'sale_start_time': '2023-01-01',
                'sale_end_time': '2023-12-31',
                'status': '上架',
                'publisher': user
            }
        )
        print(f"{'创建' if created else '使用已存在的'}测试产品: {specialty.name} (ID: {specialty.specialty_id})")
        
        # 3. 测试普通用户编辑自己的产品
        print("\n3. 测试普通用户编辑自己的产品...")
        
        # 登录普通用户
        login_result = client.login(username='testuser', password='testpass123')
        print(f"普通用户登录结果: {'成功' if login_result else '失败'}")
        
        if login_result:
            # 访问编辑页面
            response = client.get(f'/specialty/{specialty.specialty_id}/edit/')
            print(f"访问编辑页面状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ 普通用户可以访问自己产品的编辑页面")
                
                # 检查表单是否正确初始化
                soup = BeautifulSoup(response.content, 'html.parser')
                name_input = soup.find('input', {'id': 'name'})
                if name_input and name_input.get('value') == specialty.name:
                    print("✓ 表单正确初始化了产品数据")
                else:
                    print("✗ 表单未正确初始化产品数据")
                
                # 提交编辑表单
                edit_data = {
                    'origin_name': '修改后的产地',
                    'province': '修改后的省',
                    'city': '修改后的市',
                    'district': '修改后的区',
                    'category': '修改后的类别',
                    'name': '修改后的产品名',
                    'description': '修改后的产品描述',
                    'price': 199.99,
                    'sale_start_time': '2023-02-01',
                    'sale_end_time': '2023-11-30',
                    'status': '上架'
                }
                
                response = client.post(f'/specialty/{specialty.specialty_id}/edit/', data=edit_data)
                print(f"提交编辑表单状态码: {response.status_code}")
                
                if response.status_code == 302:  # 重定向表示成功
                    print("✓ 普通用户成功编辑自己的产品")
                    
                    # 验证产品是否已更新
                    updated_specialty = Specialty.objects.get(pk=specialty.specialty_id)
                    if updated_specialty.name == '修改后的产品名':
                        print("✓ 产品信息已正确更新")
                    else:
                        print("✗ 产品信息未正确更新")
                else:
                    print("✗ 普通用户编辑产品失败")
                    if response.context and 'form' in response.context:
                        form = response.context['form']
                        print(f"表单错误: {form.errors}")
            else:
                print("✗ 普通用户无法访问自己产品的编辑页面")
        
        # 4. 测试普通用户尝试编辑其他用户的产品
        print("\n4. 测试普通用户尝试编辑其他用户的产品...")
        
        # 创建另一个用户的产品
        other_user, created = User.objects.get_or_create(
            username='otheruser',
            defaults={
                'password': 'otherpass123',
                'email': 'other@example.com',
                'status': '正常'
            }
        )
        if created:
            other_user.set_password('otherpass123')
            other_user.save()
        
        other_specialty, created = Specialty.objects.get_or_create(
            name='其他用户产品',
            defaults={
                'origin': origin,
                'category': '其他类别',
                'description': '这是其他用户的测试产品',
                'price': 88.88,
                'sale_start_time': '2023-01-01',
                'sale_end_time': '2023-12-31',
                'status': '上架',
                'publisher': other_user
            }
        )
        
        # 尝试访问其他用户产品的编辑页面
        response = client.get(f'/specialty/{other_specialty.specialty_id}/edit/')
        print(f"访问其他用户产品编辑页面状态码: {response.status_code}")
        
        if response.status_code == 302:  # 重定向表示被拒绝
            print("✓ 普通用户被正确拒绝访问其他用户产品的编辑页面")
        else:
            print("✗ 普通用户未被拒绝访问其他用户产品的编辑页面")
        
        # 5. 测试管理员编辑任何产品
        print("\n5. 测试管理员编辑任何产品...")
        
        # 登出普通用户，登录管理员
        client.logout()
        login_result = client.login(username='testadmin', password='adminpass123')
        print(f"管理员登录结果: {'成功' if login_result else '失败'}")
        
        if login_result:
            # 尝试编辑其他用户的产品
            response = client.get(f'/specialty/{other_specialty.specialty_id}/edit/')
            print(f"管理员访问其他用户产品编辑页面状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ 管理员可以访问任何产品的编辑页面")
                
                # 提交编辑表单
                admin_edit_data = {
                    'origin_name': '管理员修改的产地',
                    'province': '管理员修改的省',
                    'city': '管理员修改的市',
                    'district': '管理员修改的区',
                    'category': '管理员修改的类别',
                    'name': '管理员修改的产品名',
                    'description': '管理员修改的产品描述',
                    'price': 299.99,
                    'sale_start_time': '2023-03-01',
                    'sale_end_time': '2023-10-31',
                    'status': '下架'
                }
                
                response = client.post(f'/specialty/{other_specialty.specialty_id}/edit/', data=admin_edit_data)
                print(f"管理员提交编辑表单状态码: {response.status_code}")
                
                if response.status_code == 302:  # 重定向表示成功
                    print("✓ 管理员成功编辑其他用户的产品")
                    
                    # 验证产品是否已更新
                    updated_specialty = Specialty.objects.get(pk=other_specialty.specialty_id)
                    if updated_specialty.name == '管理员修改的产品名':
                        print("✓ 产品信息已被管理员正确更新")
                    else:
                        print("✗ 产品信息未被管理员正确更新")
                else:
                    print("✗ 管理员编辑产品失败")
                    if response.context and 'form' in response.context:
                        form = response.context['form']
                        print(f"表单错误: {form.errors}")
            else:
                print("✗ 管理员无法访问其他用户产品的编辑页面")
        
        # 6. 测试冻结用户编辑产品
        print("\n6. 测试冻结用户编辑产品...")
        
        # 冻结普通用户
        user.status = '冻结'
        user.save()
        print(f"已冻结用户: {user.username}")
        
        # 重新登录冻结用户
        client.logout()
        login_result = client.login(username='testuser', password='testpass123')
        print(f"冻结用户登录结果: {'成功' if login_result else '失败'}")
        
        if login_result:
            # 尝试编辑自己的产品
            response = client.get(f'/specialty/{specialty.specialty_id}/edit/')
            print(f"冻结用户访问编辑页面状态码: {response.status_code}")
            
            if response.status_code == 302:  # 重定向表示被拒绝
                print("✓ 冻结用户被正确拒绝访问编辑页面")
            else:
                print("✗ 冻结用户未被拒绝访问编辑页面")
        
        # 恢复用户状态
        user.status = '正常'
        user.save()
        print(f"已恢复用户状态: {user.username}")
        
        # 7. 测试未登录用户访问编辑页面
        print("\n7. 测试未登录用户访问编辑页面...")
        
        client.logout()
        response = client.get(f'/specialty/{specialty.specialty_id}/edit/')
        print(f"未登录用户访问编辑页面状态码: {response.status_code}")
        
        if response.status_code == 302:  # 重定向到登录页面
            print("✓ 未登录用户被正确重定向到登录页面")
        else:
            print("✗ 未登录用户未被重定向到登录页面")
        
        print("\n" + "=" * 50)
        print("产品编辑功能测试完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_product_edit()