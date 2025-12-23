import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import hashlib


def rename_product_image(image, product_name):
    """
    重命名产品图片为产品名称，并保存到product_images目录
    
    Args:
        image: 上传的图片文件
        product_name: 产品名称
        
    Returns:
        str: 新的图片路径
    """
    if not image:
        return None
    
    # 获取文件扩展名
    file_extension = os.path.splitext(image.name)[1].lower()
    
    # 确保扩展名是有效的图片格式
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if file_extension not in valid_extensions:
        # 如果不是有效扩展名，默认使用.jpg
        file_extension = '.jpg'
    
    # 创建新的文件名：产品名称 + 扩展名
    # 确保文件名是安全的（移除可能导致问题的字符）
    safe_name = product_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    new_filename = f"{safe_name}{file_extension}"
    
    # 目标路径
    upload_path = f"product_images/{new_filename}"
    
    # 如果文件已存在，添加唯一标识符
    if default_storage.exists(upload_path):
        unique_id = str(uuid.uuid4())[:8]
        name_without_ext = os.path.splitext(new_filename)[0]
        new_filename = f"{name_without_ext}_{unique_id}{file_extension}"
        upload_path = f"product_images/{new_filename}"
    
    # 保存文件
    # 读取上传文件的内容
    image_content = image.read()
    
    # 创建新文件
    default_storage.save(upload_path, ContentFile(image_content))
    
    return upload_path


def get_product_image_path(product_name):
    """
    根据产品名称获取图片路径
    
    Args:
        product_name: 产品名称
        
    Returns:
        str: 图片路径或None
    """
    # 可能的图片扩展名
    extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    
    # 确保产品名称是安全的（移除可能导致问题的字符）
    safe_name = product_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    for ext in extensions:
        image_path = f"product_images/{safe_name}{ext}"
        if default_storage.exists(image_path):
            return image_path
    
    return None