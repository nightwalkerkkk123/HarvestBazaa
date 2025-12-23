from django import template
import os
from django.conf import settings

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def product_image(value):
    """根据产品名称获取对应的图片URL"""
    # 如果产品已有图片，直接返回
    if hasattr(value, 'image') and value.image and value.image.name != 'default-product.jpg':
        return value.image.url
    
    # 获取产品名称
    product_name = value.name if hasattr(value, 'name') else str(value)
    
    # 定义图片目录
    product_images_dir = os.path.join(settings.MEDIA_ROOT, 'product_images')
    
    # 如果目录不存在，返回默认图片
    if not os.path.exists(product_images_dir):
        return f"{settings.STATIC_URL}images/default-product.svg"
    
    # 获取目录中的所有图片文件
    image_files = [f for f in os.listdir(product_images_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    # 确保产品名称是安全的（移除可能导致问题的字符）
    safe_name = product_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    # 尝试精确匹配安全的产品名称
    for img_file in image_files:
        # 移除文件扩展名进行比较
        img_name = os.path.splitext(img_file)[0]
        if img_name == safe_name:
            return f"{settings.MEDIA_URL}product_images/{img_file}"
    
    # 尝试精确匹配原始产品名称
    for img_file in image_files:
        # 移除文件扩展名进行比较
        img_name = os.path.splitext(img_file)[0]
        if img_name == product_name:
            return f"{settings.MEDIA_URL}product_images/{img_file}"
    
    # 尝试模糊匹配（产品名称包含在图片名中或图片名包含在产品名称中）
    for img_file in image_files:
        img_name = os.path.splitext(img_file)[0].lower()
        product_lower = product_name.lower()
        safe_lower = safe_name.lower()
        
        # 检查产品名称是否包含图片名（或反之）
        if img_name in product_lower or product_lower in img_name or img_name in safe_lower or safe_lower in img_name:
            return f"{settings.MEDIA_URL}product_images/{img_file}"
    
    # 如果都没有匹配，返回默认图片
    return f"{settings.STATIC_URL}images/default-product.svg"