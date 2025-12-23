#!/usr/bin/env python
"""
检查购物车页面渲染后的HTML内容
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

def check_cart_html():
    """检查购物车页面渲染后的HTML内容"""
    print("=" * 50)
    print("检查购物车页面渲染后的HTML内容")
    print("=" * 50)
    
    # 创建测试客户端
    client = Client()
    client.defaults['HTTP_HOST'] = '127.0.0.1'
    
    try:
        # 1. 获取或创建测试用户
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
        
        # 2. 登录用户
        login_result = client.login(username='testuser_layout', password='testpass123')
        
        if login_result:
            # 3. 访问购物车页面
            response = client.get('/cart/')
            
            if response.status_code == 200:
                # 4. 提取并分析HTML内容
                content = response.content.decode('utf-8')
                
                # 查找小计金额部分
                import re
                
                # 查找表格行
                tr_pattern = r'<tr>(.*?)</tr>'
                trs = re.findall(tr_pattern, content, re.DOTALL)
                
                for i, tr in enumerate(trs):
                    if '测试布局产品' in tr:
                        print(f"\n找到产品行 {i+1}:")
                        print("-" * 30)
                        
                        # 提取各列内容
                        td_pattern = r'<td.*?>(.*?)</td>'
                        tds = re.findall(td_pattern, tr, re.DOTALL)
                        
                        if len(tds) >= 4:
                            # 产品名称
                            product_name_match = re.search(r'<h4[^>]*>(.*?)</h4>', tds[0])
                            if product_name_match:
                                print(f"产品名称: {product_name_match.group(1)}")
                            
                            # 单价
                            price_match = re.search(r'¥([\d.]+)', tds[1])
                            if price_match:
                                print(f"单价: ¥{price_match.group(1)}")
                            
                            # 数量
                            quantity_match = re.search(r'(\d+)', tds[2])
                            if quantity_match:
                                print(f"数量: {quantity_match.group(1)}")
                            
                            # 小计
                            subtotal_match = re.search(r'¥([\d.]+)', tds[3])
                            if subtotal_match:
                                print(f"小计: ¥{subtotal_match.group(1)}")
                                
                                # 验证小计是否正确
                                price = float(price_match.group(1)) if price_match else 0
                                quantity = int(quantity_match.group(1)) if quantity_match else 0
                                expected_subtotal = price * quantity
                                actual_subtotal = float(subtotal_match.group(1))
                                
                                if abs(expected_subtotal - actual_subtotal) < 0.01:
                                    print(f"✓ 小计计算正确: {price} × {quantity} = {actual_subtotal}")
                                else:
                                    print(f"✗ 小计计算错误: 预期 {expected_subtotal}, 实际 {actual_subtotal}")
                
                # 查找总金额
                total_match = re.search(r'总金额:.*?¥([\d.]+)', content)
                if total_match:
                    print(f"\n总金额: ¥{total_match.group(1)}")
                
                print("\n" + "=" * 50)
                print("HTML内容检查完成")
                print("=" * 50)
            else:
                print(f"访问购物车页面失败，状态码: {response.status_code}")
        else:
            print("用户登录失败")
        
    except Exception as e:
        print(f"检查过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_cart_html()