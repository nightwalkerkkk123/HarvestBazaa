#!/usr/bin/env python
"""
测试图片匹配功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from market.templatetags.market_filters import product_image
from market.models import Specialty
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from market.utils import rename_product_image

def test_image_matching():
    """测试图片匹配功能"""
    print("开始测试图片匹配功能...")
    
    # 测试用例
    test_cases = [
        ("苹果", "apple.jpg"),
        ("进口香蕉", "banana.png"),
        ("有机蔬菜", "vegetables.jpeg"),
        ("新鲜水果", "fresh_fruit.gif"),
        ("地方特产", "local_specialty.webp"),
        ("测试产品/名称", "test_product.jpg"),
        ("测试:产品*名称", "test_special.jpg"),
    ]
    
    # 创建测试图片
    print("\n创建测试图片...")
    for product_name, original_filename in test_cases:
        print(f"\n测试产品: {product_name}, 原始文件: {original_filename}")
        
        # 创建一个模拟的上传文件
        test_content = b"fake image content for testing"
        uploaded_file = SimpleUploadedFile(
            name=original_filename,
            content=test_content,
            content_type="image/jpeg"
        )
        
        # 调用重命名函数
        try:
            new_path = rename_product_image(uploaded_file, product_name)
            print(f"  重命名成功: {new_path}")
        except Exception as e:
            print(f"  错误: {str(e)}")
    
    # 测试图片匹配
    print("\n测试图片匹配功能...")
    
    # 创建模拟的产品对象
    class MockProduct:
        def __init__(self, name):
            self.name = name
            self.image = None
    
    for product_name, _ in test_cases:
        print(f"\n测试产品: {product_name}")
        
        # 创建模拟产品对象
        mock_product = MockProduct(product_name)
        
        # 使用过滤器获取图片URL
        image_url = product_image(mock_product)
        print(f"  匹配到的图片URL: {image_url}")
        
        # 检查是否匹配成功
        if "default-product.svg" in image_url:
            print(f"  匹配结果: 失败（使用默认图片）")
        else:
            print(f"  匹配结果: 成功")
    
    # 清理测试文件
    print("\n清理测试文件...")
    try:
        if default_storage.exists('product_images'):
            test_files = [
                "苹果.jpg", "进口香蕉.png", "有机蔬菜.jpeg", 
                "新鲜水果.gif", "地方特产.webp", 
                "测试产品_名称.jpg", "测试_产品_名称.jpg"
            ]
            
            for filename in test_files:
                file_path = f"product_images/{filename}"
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                    print(f"  已删除: {file_path}")
            
            # 检查并删除可能带有UUID的文件
            _, files = default_storage.listdir('product_images')
            for file in files:
                if any(test_name in file for test_name, _ in test_cases):
                    default_storage.delete(f"product_images/{file}")
                    print(f"  已删除UUID文件: {file}")
    except Exception as e:
        print(f"  清理错误: {str(e)}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_image_matching()