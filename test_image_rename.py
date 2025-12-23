#!/usr/bin/env python
"""
测试图片重命名功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from market.utils import rename_product_image, get_product_image_path
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
import shutil

def test_image_rename():
    """测试图片重命名功能"""
    print("开始测试图片重命名功能...")
    
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
            
            # 检查文件是否存在
            if new_path and default_storage.exists(new_path):
                print(f"  文件存在: 是")
                
                # 检查获取路径函数
                found_path = get_product_image_path(product_name)
                print(f"  通过产品名称找到路径: {found_path}")
                
                # 验证路径是否匹配
                if found_path == new_path:
                    print(f"  路径匹配: 是")
                else:
                    print(f"  路径匹配: 否")
            else:
                print(f"  文件存在: 否")
        except Exception as e:
            print(f"  错误: {str(e)}")
    
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
    test_image_rename()