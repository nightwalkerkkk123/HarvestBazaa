#!/usr/bin/env python
"""
测试脚本：验证产品发布表单样式是否与登录表单一致
"""

import os
import sys
import re
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_product_form_styling():
    """测试产品发布表单的样式"""
    print("=" * 60)
    print("测试产品发布表单样式")
    print("=" * 60)
    
    # 创建测试用户
    username = 'testuser_form_style'
    password = 'testpassword123'
    
    # 删除已存在的测试用户
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
    
    # 创建新用户
    user = User.objects.create_user(
        username=username,
        email='test@example.com',
        password=password
    )
    
    # 创建客户端并登录
    client = Client()
    
    # 先登录
    login_url = reverse('login')
    login_response = client.post(login_url, {
        'username': username,
        'password': password
    })
    
    if login_response.status_code != 302:
        print("登录失败，无法继续测试")
        return False
    
    # 获取产品发布页面
    publish_url = reverse('publish_specialty')
    response = client.get(publish_url)
    
    if response.status_code != 200:
        print(f"获取产品发布页面失败，状态码: {response.status_code}")
        return False
    
    content = response.content.decode('utf-8')
    
    # 检查是否使用了auth-container类
    if 'auth-container' in content:
        print("✓ 产品表单使用了auth-container类")
    else:
        print("✗ 产品表单未使用auth-container类")
    
    # 检查是否使用了auth-card类
    if 'auth-card' in content:
        print("✓ 产品表单使用了auth-card类")
    else:
        print("✗ 产品表单未使用auth-card类")
    
    # 检查是否使用了auth-header类
    if 'auth-header' in content:
        print("✓ 产品表单使用了auth-header类")
    else:
        print("✗ 产品表单未使用auth-header类")
    
    # 检查是否使用了auth-title类
    if 'auth-title' in content:
        print("✓ 产品表单使用了auth-title类")
    else:
        print("✗ 产品表单未使用auth-title类")
    
    # 检查是否使用了auth-subtitle类
    if 'auth-subtitle' in content:
        print("✓ 产品表单使用了auth-subtitle类")
    else:
        print("✗ 产品表单未使用auth-subtitle类")
    
    # 检查是否使用了auth-form类
    if 'auth-form' in content:
        print("✓ 产品表单使用了auth-form类")
    else:
        print("✗ 产品表单未使用auth-form类")
    
    # 检查是否使用了form-group类
    if 'form-group' in content:
        print("✓ 产品表单使用了form-group类")
    else:
        print("✗ 产品表单未使用form-group类")
    
    # 检查是否使用了form-label类
    if 'form-label' in content:
        print("✓ 产品表单使用了form-label类")
    else:
        print("✗ 产品表单未使用form-label类")
    
    # 检查是否使用了form-control类
    if 'form-control' in content:
        print("✓ 产品表单使用了form-control类")
    else:
        print("✗ 产品表单未使用form-control类")
    
    # 检查是否使用了btn-primary btn-block类
    if 'btn-primary btn-block' in content:
        print("✓ 产品表单使用了btn-primary btn-block类")
    else:
        print("✗ 产品表单未使用btn-primary btn-block类")
    
    # 检查是否设置了背景色为#f8f9fa
    if 'background-color: #f8f9fa' in content:
        print("✓ 产品表单页面设置了与登录页面相同的背景色")
    else:
        print("✗ 产品表单页面未设置与登录页面相同的背景色")
    
    # 获取登录页面内容进行对比
    login_response = client.get(reverse('login'))
    login_content = login_response.content.decode('utf-8')
    
    # 检查两个页面是否都使用了相同的CSS类
    auth_classes = ['auth-container', 'auth-card', 'auth-header', 'auth-title', 'auth-subtitle', 'auth-form']
    all_match = True
    
    for css_class in auth_classes:
        if css_class in login_content and css_class in content:
            print(f"✓ 登录页面和产品发布页面都使用了{css_class}类")
        else:
            print(f"✗ 登录页面和产品发布页面未同时使用{css_class}类")
            all_match = False
    
    # 清理测试数据
    user.delete()
    
    print("\n" + "=" * 60)
    if all_match:
        print("测试结果：产品发布表单样式与登录表单一致")
    else:
        print("测试结果：产品发布表单样式与登录表单不完全一致")
    print("=" * 60)
    
    return all_match

if __name__ == "__main__":
    success = test_product_form_styling()
    sys.exit(0 if success else 1)