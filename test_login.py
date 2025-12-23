#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from market.models import User
from market.forms import LoginForm
from django.test import RequestFactory
from market.views import user_login

# 检查用户是否存在
try:
    user = User.objects.get(username='bad_user_test')
    print(f"找到用户: {user.username}, 状态: {user.status}")
    print(f"密码验证结果: {user.check_password('123456')}")
except User.DoesNotExist:
    print("用户不存在")
    sys.exit(1)

# 创建请求工厂
factory = RequestFactory()

# 创建登录请求
request = factory.post('/login/', {
    'username': 'bad_user_test',
    'password': '123456',
    'csrfmiddlewaretoken': 'test-token'
})

# 调用登录视图
response = user_login(request)

# 检查响应
print(f"响应状态码: {response.status_code}")
print(f"响应内容类型: {response['Content-Type']}")

# 检查响应内容
content = response.content.decode('utf-8')

# 检查弹窗标志
# 注意：show_frozen_modal是模板变量，不会出现在最终HTML中
# 我们通过检查showModal()是否被调用来判断弹窗是否应该显示
if 'showModal();' in content:
    print("✓ 成功检测到冻结用户弹窗触发（showModal()被调用）")
else:
    print("✗ 未检测到冻结用户弹窗触发")

# 检查弹窗HTML结构
if 'frozenModal' in content:
    print("✓ 成功检测到冻结弹窗HTML结构")
else:
    print("✗ 未检测到冻结弹窗HTML结构")

# 检查错误消息
if '您的账户已被冻结' in content:
    print("✓ 成功检测到冻结错误消息")
else:
    print("✗ 未检测到冻结错误消息")

# 检查弹窗显示JavaScript
if 'showModal()' in content:
    print("✓ 成功检测到弹窗显示JavaScript")
else:
    print("✗ 未检测到弹窗显示JavaScript")
    
# 打印部分响应内容用于调试
print("\n响应内容片段:")
print(content[:1000])

# 查找show_frozen_modal模板渲染
print("\n查找show_frozen_modal模板渲染部分:")
import re
match = re.search(r'document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{([^}]+)\}', content)
if match:
    print(match.group(0))
else:
    print("未找到DOMContentLoaded事件监听器")