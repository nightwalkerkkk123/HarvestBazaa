from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import date
from .models import *
from .forms import UserRegistrationForm, LoginForm, SpecialtyForm, SpecialtyEditForm, OrderForm
from .utils import rename_product_image

# 用户注册
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'market/register.html', {'form': form})

# 用户登录
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print(f"表单验证结果: {form.is_valid()}")
        if not form.is_valid():
            print(f"表单错误: {form.errors}")
            return render(request, 'market/login.html', {'form': form, 'error_message': '用户名或密码错误'})
        
        # 表单验证通过，获取表单数据
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        print(f"表单数据 - 用户名: {username}, 密码: {password}")
        
        # 直接查询用户，绕过Django的is_active检查
        try:
            user = User.objects.get(username=username)
            print(f"找到用户: {user.username}, 状态: {user.status}")
            
            # 检查用户状态
            if user.status == '冻结':
                print("用户状态为冻结，返回冻结页面")
                return render(request, 'market/login.html', {
                    'form': form, 
                    'error_message': '您的账户已被冻结，请联系管理员',
                    'show_frozen_modal': True  # 添加标志以显示弹窗
                })
            
            # 登录用户
            from django.contrib.auth import login
            login(request, user)
            return redirect('index')
            
        except User.DoesNotExist:
            print("用户不存在")
            return render(request, 'market/login.html', {'form': form, 'error_message': '用户名或密码错误'})
    else:
        form = LoginForm()
    return render(request, 'market/login.html', {'form': form})

# 用户登出
def user_logout(request):
    logout(request)
    return redirect('index')

# 首页（加载Vue.js应用）
def index(request):
    # 获取搜索查询参数
    search_query = request.GET.get('search', '')
    
    # 获取分类筛选参数
    category = request.GET.get('category', '')
    
    # 获取所有在售的特色产品
    specialties = Specialty.objects.filter(status='上架')
    
    # 如果有搜索查询，按产品名称过滤
    if search_query:
        specialties = specialties.filter(name__icontains=search_query)
    
    # 如果有分类筛选，按分类过滤
    if category:
        specialties = specialties.filter(category=category)
    
    # 调试信息
    print(f"搜索查询: {search_query}")
    print(f"分类筛选: {category}")
    print(f"找到的产品数量: {specialties.count()}")
    for s in specialties[:3]:  # 只打印前3个产品
        print(f"  - {s.name} (ID: {s.specialty_id})")
    
    # 获取所有分类选项
    categories = Specialty.objects.values_list('category', flat=True).distinct()
    
    # 返回Vue.js应用的index.html文件
    return render(request, 'market/index.html', {
        'specialties': specialties,
        'search_query': search_query,
        'selected_category': category,
        'categories': categories
    })

# Vue.js API接口
from django.http import JsonResponse

def classification_list(request):
    """返回分类列表API"""
    # 直接返回符合a-tree组件要求的格式（包含key和title字段）
    classifications = [
        {"id": 1, "name": "茶叶", "icon": "food", "key": "1", "title": "茶叶"},
        {"id": 2, "name": "粮油", "icon": "food", "key": "2", "title": "粮油"},
        {"id": 3, "name": "水果", "icon": "food", "key": "3", "title": "水果"},
        {"id": 4, "name": "水产", "icon": "food", "key": "4", "title": "水产"},
        {"id": 5, "name": "干果", "icon": "food", "key": "5", "title": "干果"},
        {"id": 6, "name": "其他", "icon": "food", "key": "6", "title": "其他"},
    ]
    return JsonResponse({"code": 200, "data": classifications, "message": "成功"})

def tag_list(request):
    """返回标签列表API"""
    # 模拟标签数据
    tags = [
        {"id": 1, "name": "热门"},
        {"id": 2, "name": "新品"},
        {"id": 3, "name": "限时特惠"},
        {"id": 4, "name": "人气爆款"},
    ]
    return JsonResponse({"code": 200, "data": tags, "message": "成功"})

def thing_list(request):
    """返回商品列表API，支持sort和c参数"""
    sort = request.GET.get('sort', 'hot')
    category_id = request.GET.get('c', '-1')
    
    # 获取数据库中的商品数据
    specialties = Specialty.objects.filter(status='上架')
    
    # 转换为前端需要的格式
    things = []
    for s in specialties:
        thing = {
            "id": s.specialty_id,
            "title": s.name,
            "price": float(s.price),
            "image": "img/default-product.jpg",  # 默认图片，可根据实际情况调整
            "description": s.description,
            "sales": 100,  # 销量数据，可根据实际情况调整
            "category_id": get_category_id(s.category),  # 将类别转换为ID
            "tags": [1],  # 默认标签，可根据实际情况调整
            "origin": s.origin.origin_name,
            "province": s.origin.province,
            "city": s.origin.city,
            "publisher": s.publisher.username,
            "sale_start_time": s.sale_start_time.strftime("%Y-%m-%d") if s.sale_start_time else "",
            "sale_end_time": s.sale_end_time.strftime("%Y-%m-%d") if s.sale_end_time else "",
        }
        things.append(thing)
    
    # 根据分类ID过滤
    if category_id != '-1':
        things = [t for t in things if t['category_id'] == int(category_id)]
    
    # 根据排序参数排序
    if sort == 'hot':
        things.sort(key=lambda x: x['sales'], reverse=True)
    elif sort == 'new':
        things.sort(key=lambda x: x['id'], reverse=True)
    elif sort == 'price_asc':
        things.sort(key=lambda x: x['price'])
    elif sort == 'price_desc':
        things.sort(key=lambda x: x['price'], reverse=True)
    
    return JsonResponse({"code": 200, "data": things, "message": "成功"})

def get_category_id(category_name):
    """将类别名称转换为ID"""
    category_map = {
        "茶叶": 1,
        "粮油": 2,
        "水果": 3,
        "水产": 4,
        "干果": 5,
        "其他": 6
    }
    return category_map.get(category_name, 6)  # 默认返回"其他"类别的ID

def products_view(request):
    """展示商品列表页面"""
    return render(request, 'products.html')

def product_detail_view(request):
    """渲染商品详情页面"""
    return render(request, 'product_detail.html')

def thing_detail(request, thing_id):
    """返回单个商品详情API"""
    try:
        specialty = Specialty.objects.get(specialty_id=thing_id)
        
        # 转换为前端需要的格式
        thing = {
            "id": specialty.specialty_id,
            "title": specialty.name,
            "price": float(specialty.price),
            "image": "/static/img/default-product.jpg",  # 默认图片，可根据实际情况调整
            "description": specialty.description,
            "sales": 100,  # 销量数据，可根据实际情况调整
            "category_id": get_category_id(specialty.category),  # 将类别转换为ID
            "category": specialty.category,
            "tags": [1],  # 默认标签，可根据实际情况调整
            "origin": specialty.origin.origin_name,
            "province": specialty.origin.province,
            "city": specialty.origin.city,
            "district": specialty.origin.district,
            "publisher": specialty.publisher.username,
            "publisher_id": specialty.publisher.user_id,
            "sale_start_time": specialty.sale_start_time.strftime("%Y-%m-%d") if specialty.sale_start_time else "",
            "sale_end_time": specialty.sale_end_time.strftime("%Y-%m-%d") if specialty.sale_end_time else "",
            "create_time": specialty.create_time.strftime("%Y-%m-%d %H:%M:%S") if specialty.create_time else "",
            "status": specialty.status,
        }
        
        return JsonResponse({"code": 200, "data": thing, "message": "成功"})
    except Specialty.DoesNotExist:
        return JsonResponse({"code": 404, "data": None, "message": "商品不存在"})

def thing_detail_query(request):
    """返回单个商品详情API，通过查询参数获取商品ID"""
    thing_id = request.GET.get('id')
    if not thing_id:
        return JsonResponse({"code": 400, "data": None, "message": "缺少商品ID参数"})
    
    try:
        specialty = Specialty.objects.get(specialty_id=thing_id)
        
        # 转换为前端需要的格式
        thing = {
            "id": specialty.specialty_id,
            "title": specialty.name,
            "price": float(specialty.price),
            "image": "/static/img/default-product.jpg",  # 默认图片，可根据实际情况调整
            "description": specialty.description,
            "sales": 100,  # 销量数据，可根据实际情况调整
            "category_id": get_category_id(specialty.category),  # 将类别转换为ID
            "category": specialty.category,
            "tags": [1],  # 默认标签，可根据实际情况调整
            "origin": specialty.origin.origin_name,
            "province": specialty.origin.province,
            "city": specialty.origin.city,
            "district": specialty.origin.district,
            "publisher": specialty.publisher.username,
            "publisher_id": specialty.publisher.user_id,
            "sale_start_time": specialty.sale_start_time.strftime("%Y-%m-%d") if specialty.sale_start_time else "",
            "sale_end_time": specialty.sale_end_time.strftime("%Y-%m-%d") if specialty.sale_end_time else "",
            "create_time": specialty.create_time.strftime("%Y-%m-%d %H:%M:%S") if specialty.create_time else "",
            "status": specialty.status,
        }
        
        return JsonResponse({"code": 200, "data": thing, "message": "成功"})
    except Specialty.DoesNotExist:
        return JsonResponse({"code": 404, "data": None, "message": "商品不存在"})

def notice_list_api(request):
    """返回公告列表API"""
    # 模拟公告数据
    notices = [
        {
            "id": 1,
            "title": "网站上线公告",
            "content": "欢迎使用特产交易系统，我们致力于为您提供最优质的特产商品。",
            "create_time": "2025-12-01 10:00:00"
        },
        {
            "id": 2,
            "title": "双十二促销活动",
            "content": "双十二期间全场商品八折优惠，欢迎选购！",
            "create_time": "2025-12-10 14:30:00"
        },
    ]
    return JsonResponse({"code": 200, "data": notices, "message": "成功"})

def comment_list(request):
    """返回评论列表API"""
    thing_id = request.GET.get('thingId')
    order = request.GET.get('order', 'recent')
    
    if not thing_id:
        return JsonResponse({"code": 400, "data": None, "message": "缺少商品ID参数"})
    
    try:
        # 获取商品
        specialty = Specialty.objects.get(specialty_id=thing_id)
        
        # 模拟评论数据（实际项目中应该从数据库获取）
        comments = [
            {
                "id": 1,
                "content": "这个特产质量很好，物超所值！",
                "user": {
                    "id": 1,
                    "username": "张三",
                    "avatar": "/static/img/default-avatar.jpg"
                },
                "thing": thing_id,
                "like_count": 5,
                "create_time": "2025-12-20 10:00:00"
            },
            {
                "id": 2,
                "content": "包装很精美，送人很有面子。",
                "user": {
                    "id": 2,
                    "username": "李四",
                    "avatar": "/static/img/default-avatar.jpg"
                },
                "thing": thing_id,
                "like_count": 3,
                "create_time": "2025-12-19 15:30:00"
            },
            {
                "id": 3,
                "content": "味道很正宗，和在当地吃的一样。",
                "user": {
                    "id": 3,
                    "username": "王五",
                    "avatar": "/static/img/default-avatar.jpg"
                },
                "thing": thing_id,
                "like_count": 8,
                "create_time": "2025-12-18 09:15:00"
            }
        ]
        
        # 根据排序参数排序
        if order == 'recent':
            comments.sort(key=lambda x: x['create_time'], reverse=True)
        elif order == 'hot':
            comments.sort(key=lambda x: x['like_count'], reverse=True)
        
        return JsonResponse({"code": 200, "data": comments, "message": "成功"})
    except Specialty.DoesNotExist:
        return JsonResponse({"code": 404, "data": None, "message": "商品不存在"})

def create_comment(request):
    """创建评论API"""
    if request.method == 'POST':
        content = request.POST.get('content')
        thing_id = request.POST.get('thing')
        user_id = request.POST.get('user')
        
        if not all([content, thing_id, user_id]):
            return JsonResponse({"code": 400, "data": None, "message": "缺少必要参数"})
        
        try:
            # 验证商品是否存在
            specialty = Specialty.objects.get(specialty_id=thing_id)
            # 验证用户是否存在
            user = User.objects.get(user_id=user_id)
            
            # 在实际项目中，这里应该创建评论记录到数据库
            # 由于模型中没有评论表，这里返回模拟数据
            comment = {
                "id": 4,
                "content": content,
                "user": {
                    "id": user_id,
                    "username": user.username,
                    "avatar": "/static/img/default-avatar.jpg"
                },
                "thing": thing_id,
                "like_count": 0,
                "create_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return JsonResponse({"code": 200, "data": comment, "message": "评论成功"})
        except (Specialty.DoesNotExist, User.DoesNotExist):
            return JsonResponse({"code": 404, "data": None, "message": "商品或用户不存在"})
    
    return JsonResponse({"code": 405, "data": None, "message": "请求方法不允许"})

def like_comment(request):
    """点赞评论API"""
    if request.method == 'POST':
        comment_id = request.POST.get('commentId')
        
        if not comment_id:
            return JsonResponse({"code": 400, "data": None, "message": "缺少评论ID参数"})
        
        # 在实际项目中，这里应该更新评论的点赞数到数据库
        # 由于模型中没有评论表，这里返回模拟数据
        return JsonResponse({"code": 200, "data": {"like_count": 10}, "message": "点赞成功"})
    
    return JsonResponse({"code": 405, "data": None, "message": "请求方法不允许"})

def list_my_comments(request):
    """返回我的评论列表API"""
    # 在实际项目中，这里应该从数据库获取用户的评论
    # 由于模型中没有评论表，这里返回空列表
    return JsonResponse({"code": 200, "data": [], "message": "成功"})

# 产品详情页
def specialty_detail(request, specialty_id):
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    return render(request, 'market/specialty_detail.html', {'specialty': specialty})

# 用户发布产品（需要登录）
@login_required
def publish_specialty(request):
    """
    发布特色时令产品
    任何已登录的普通用户都可以发布产品
    """
    # 检查用户状态
    if request.user.status == '冻结':
        messages.error(request, '您的账户已被冻结，无法发布产品')
        return redirect('index')
    
    if request.method == 'POST':
        form = SpecialtyForm(request.POST, request.FILES)
        
        # 添加调试信息
        print(f"表单是否有效: {form.is_valid()}")
        if not form.is_valid():
            print(f"表单错误: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        if form.is_valid():
            # 获取表单数据
            origin_name = form.cleaned_data.get('origin_name')
            province = form.cleaned_data.get('province')
            city = form.cleaned_data.get('city')
            district = form.cleaned_data.get('district')
            category = form.cleaned_data.get('category')
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            price = form.cleaned_data.get('price')
            sale_start_time = form.cleaned_data.get('sale_start_time')
            sale_end_time = form.cleaned_data.get('sale_end_time')
            image = form.cleaned_data.get('image')
            
            print(f"准备创建产品: {name}, 类别: {category}, 价格: {price}")
            
            try:
                # 创建或获取产地
                origin, created = Origin.objects.get_or_create(
                    province=province,
                    city=city,
                    district=district,
                    defaults={'origin_name': origin_name}
                )
                print(f"产地{'创建' if created else '获取'}成功: {origin.origin_name}")
                
                # 创建特产，默认状态为上架
                specialty = Specialty.objects.create(
                    publisher=request.user,
                    origin=origin,
                    category=category,
                    name=name,
                    description=description,
                    price=price,
                    sale_start_time=sale_start_time,
                    sale_end_time=sale_end_time,
                    status='上架'  # 默认状态为上架
                )
                print(f"产品创建成功，ID: {specialty.specialty_id}")
                
                # 如果有图片，则重命名并更新图片
                if image:
                    # 使用自定义函数重命名图片
                    new_image_path = rename_product_image(image, name)
                    if new_image_path:
                        specialty.image = new_image_path
                        specialty.save()
                        print(f"产品图片重命名并更新成功: {new_image_path}")
                    else:
                        print("产品图片重命名失败")
                
                messages.success(request, '产品发布成功！')
                return redirect('user_specialties')
            except Exception as e:
                print(f"创建产品时出错: {str(e)}")
                messages.error(request, f'发布产品时出错: {str(e)}')
    else:
        form = SpecialtyForm()
    
    return render(request, 'market/publish_specialty.html', {'form': form})

# 用户下架/上架自己的产品（需要登录）
@login_required
def toggle_specialty_status(request, specialty_id):
    """
    用户下架/上架自己的产品
    只有产品发布者可以操作
    """
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    
    # 检查用户状态
    if request.user.status == '冻结':
        messages.error(request, '您的账户已被冻结，无法进行此操作')
        return redirect('user_specialties')
    
    # 只有产品发布者可以操作
    if specialty.publisher == request.user:
        old_status = specialty.status
        specialty.status = '下架' if specialty.status == '上架' else '上架'
        specialty.save()
        
        # 添加操作成功消息
        if old_status == '上架':
            messages.success(request, f'产品 "{specialty.name}" 已成功下架')
        else:
            messages.success(request, f'产品 "{specialty.name}" 已重新上架')
    else:
        messages.error(request, '您没有权限操作此产品')
    
    return redirect('user_specialties')

# 用户删除自己的产品（需要登录）
@login_required
def delete_specialty(request, specialty_id):
    """
    用户删除自己的产品
    只有产品发布者可以操作
    """
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    
    # 检查用户状态
    if request.user.status == '冻结':
        messages.error(request, '您的账户已被冻结，无法进行此操作')
        return redirect('user_specialties')
    
    # 只有产品发布者可以操作
    if specialty.publisher == request.user:
        specialty_name = specialty.name
        specialty.delete()
        messages.success(request, f'产品 "{specialty_name}" 已成功删除')
    else:
        messages.error(request, '您没有权限删除此产品')
    
    return redirect('user_specialties')

# 编辑产品（需要登录）
@login_required
def edit_specialty(request, specialty_id):
    """
    编辑产品信息
    产品发布者和管理员可以编辑
    """
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    
    # 检查用户状态
    if request.user.status == '冻结':
        messages.error(request, '您的账户已被冻结，无法进行此操作')
        return redirect('user_specialties' if specialty.publisher == request.user else 'admin_specialties')
    
    # 检查权限：只有产品发布者或管理员可以编辑
    is_admin = request.user.is_staff or request.user.is_superuser
    if not (specialty.publisher == request.user or is_admin):
        messages.error(request, '您没有权限编辑此产品')
        return redirect('specialty_detail', specialty_id=specialty_id)
    
    if request.method == 'POST':
        form = SpecialtyEditForm(request.POST, request.FILES)
        
        # 添加调试信息
        print(f"表单是否有效: {form.is_valid()}")
        if not form.is_valid():
            print(f"表单错误: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        if form.is_valid():
            # 获取表单数据
            origin_name = form.cleaned_data.get('origin_name')
            province = form.cleaned_data.get('province')
            city = form.cleaned_data.get('city')
            district = form.cleaned_data.get('district')
            category = form.cleaned_data.get('category')
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            price = form.cleaned_data.get('price')
            sale_start_time = form.cleaned_data.get('sale_start_time')
            sale_end_time = form.cleaned_data.get('sale_end_time')
            status = form.cleaned_data.get('status')
            image = form.cleaned_data.get('image')
            
            try:
                # 创建或获取产地
                origin, created = Origin.objects.get_or_create(
                    province=province,
                    city=city,
                    district=district,
                    defaults={'origin_name': origin_name}
                )
                print(f"产地{'创建' if created else '获取'}成功: {origin.origin_name}")
                
                # 更新产品信息
                specialty.origin = origin
                specialty.category = category
                specialty.name = name
                specialty.description = description
                specialty.price = price
                specialty.sale_start_time = sale_start_time
                specialty.sale_end_time = sale_end_time
                specialty.status = status
                
                # 如果有新图片，则更新
                if image:
                    # 使用自定义函数重命名图片
                    new_image_path = rename_product_image(image, name)
                    if new_image_path:
                        specialty.image = new_image_path
                        print(f"产品图片重命名并更新成功: {new_image_path}")
                    else:
                        print("产品图片重命名失败")
                
                specialty.save()
                print(f"产品更新成功，ID: {specialty.specialty_id}")
                
                messages.success(request, '产品信息更新成功！')
                return redirect('specialty_detail', specialty_id=specialty.specialty_id)
            except Exception as e:
                print(f"更新产品时出错: {str(e)}")
                messages.error(request, f'更新产品时出错: {str(e)}')
    else:
        # 初始化表单，填充现有数据
        initial_data = {
            'origin_name': specialty.origin.origin_name,
            'province': specialty.origin.province,
            'city': specialty.origin.city,
            'district': specialty.origin.district,
            'category': specialty.category,
            'name': specialty.name,
            'description': specialty.description,
            'price': specialty.price,
            'sale_start_time': specialty.sale_start_time,
            'sale_end_time': specialty.sale_end_time,
            'status': specialty.status,
        }
        form = SpecialtyEditForm(initial=initial_data)
    
    # 确定返回URL
    back_url = 'user_specialties' if specialty.publisher == request.user else 'admin_specialties'
    
    return render(request, 'market/edit_specialty.html', {
        'form': form, 
        'specialty': specialty,
        'is_admin': is_admin,
        'back_url': back_url
    })

# 用户查看自己发布的产品（需要登录）
@login_required
def user_specialties(request):
    specialties = Specialty.objects.filter(publisher=request.user)
    return render(request, 'market/user_specialties.html', {'specialties': specialties})

# 添加到购物车（需要登录）
@login_required
def add_to_cart(request, specialty_id):
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # 检查是否已在购物车中
    cart_item, created = ShoppingCart.objects.get_or_create(
        user=request.user,
        specialty=specialty,
        defaults={'quantity': quantity}
    )
    
    # 如果已存在，则增加数量
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return redirect('shopping_cart')

# 查看购物车（需要登录）
@login_required
def shopping_cart(request):
    cart_items = ShoppingCart.objects.filter(user=request.user)
    # 计算总金额
    total_amount = sum(item.specialty.price * item.quantity for item in cart_items)
    return render(request, 'market/shopping_cart.html', {'cart_items': cart_items, 'total_amount': total_amount})

# 删除购物车商品（需要登录）
@login_required
def delete_cart_item(request, cart_id):
    cart_item = get_object_or_404(ShoppingCart, pk=cart_id)
    if cart_item.user == request.user:
        cart_item.delete()
    return redirect('shopping_cart')

# 创建订单（需要登录）
@login_required
def create_order(request):
    # 获取购物车中的商品
    cart_items = ShoppingCart.objects.filter(user=request.user)
    if not cart_items:
        return redirect('shopping_cart')
    
    # 计算总价和每个商品的小计
    total_amount = 0
    for item in cart_items:
        item.subtotal = item.specialty.price * item.quantity
        total_amount += item.subtotal
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # 创建订单
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount
            )
            
            # 创建订单项
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    specialty=item.specialty,
                    quantity=item.quantity,
                    unit_price=item.specialty.price
                )
            
            # 清空购物车
            cart_items.delete()
            
            # 显示下单成功消息
            return render(request, 'market/order_success.html', {'order': order})
    else:
        form = OrderForm()
    
    return render(request, 'market/create_order.html', {'form': form, 'cart_items': cart_items, 'total_amount': total_amount})

# 订单详情（需要登录）
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    # 只有订单所有者可以查看
    if order.user != request.user:
        return redirect('index')
    
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'market/order_detail.html', {'order': order, 'order_items': order_items})

# 用户订单列表（需要登录）
@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    # 为每个订单获取第一个产品信息
    for order in orders:
        first_item = order.orderitem_set.first()
        if first_item:
            order.first_item_specialty = first_item.specialty
            order.first_item_name = first_item.specialty.name
        else:
            order.first_item_specialty = None
            order.first_item_name = "无产品"
    
    return render(request, 'market/user_orders.html', {'orders': orders})

# 收藏产品（需要登录）
@login_required
def collect_specialty(request, specialty_id):
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    
    # 检查是否已收藏
    collection, created = Collection.objects.get_or_create(
        user=request.user,
        specialty=specialty
    )
    
    return redirect('user_collections')

# 取消收藏（需要登录）
@login_required
def cancel_collect(request, collect_id):
    collection = get_object_or_404(Collection, pk=collect_id)
    if collection.user == request.user:
        collection.delete()
    return redirect('user_collections')

# 用户收藏列表（需要登录）
@login_required
def user_collections(request):
    collections = Collection.objects.filter(user=request.user)
    return render(request, 'market/user_collections.html', {'collections': collections})

# 提交投诉（需要登录）
@login_required
def submit_complaint(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.user != request.user:
        messages.error(request, '您只能对自己的订单提交投诉')
        return redirect('index')
    
    # 检查订单状态是否允许投诉
    if order.status not in ['已支付', '已完成']:
        messages.error(request, '只有已支付或已完成的订单才能提交投诉')
        return redirect('order_detail', order_id=order_id)
    
    # 检查是否已经投诉过
    if Complaint.objects.filter(order=order, user=request.user).exists():
        messages.warning(request, '您已经对该订单提交过投诉')
        return redirect('order_detail', order_id=order_id)
    
    if request.method == 'POST':
        complaint_type = request.POST.get('complaint_type')
        reason = request.POST.get('reason')
        
        # 验证投诉原因不能为空
        if not reason or not reason.strip():
            messages.error(request, '投诉原因不能为空')
            return render(request, 'market/submit_complaint.html', {'order': order})
        
        # 创建投诉
        Complaint.objects.create(
            order=order,
            user=request.user,
            complaint_type=complaint_type,
            reason=reason
        )
        
        messages.success(request, '投诉提交成功，我们会尽快处理')
        return redirect('user_orders')
    
    return render(request, 'market/submit_complaint.html', {'order': order})

# 支付订单（需要登录）
@login_required
def pay_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.user != request.user:
        messages.error(request, '您只能支付自己的订单')
        return redirect('index')
    
    # 检查订单状态是否允许支付
    if order.status != '待支付':
        messages.error(request, '只有待支付的订单才能进行支付')
        return redirect('order_detail', order_id=order_id)
    
    if request.method == 'POST':
        # 更新订单状态为已支付
        order.status = '已支付'
        order.pay_time = timezone.now()  # 设置支付时间
        order.save()
        
        messages.success(request, '订单支付成功！')
        return redirect('order_detail', order_id=order_id)
    
    return render(request, 'market/pay_order.html', {'order': order})

# 检查用户是否为管理员
def is_admin(user):
    return user.role == '管理员' and user.status == '正常'

# 管理员查看待处理投诉（需要管理员权限）
@login_required
@user_passes_test(is_admin)
def admin_complaints(request):
    complaints = Complaint.objects.filter(status='待处理')
    return render(request, 'market/admin_complaints.html', {'complaints': complaints})

# 管理员处理投诉（需要管理员权限）
@login_required
@user_passes_test(is_admin)
def handle_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    
    if request.method == 'POST':
        opinion = request.POST.get('opinion')
        
        # 创建处理记录
        ComplaintHandle.objects.create(
            complaint=complaint,
            admin=request.user,
            opinion=opinion
        )
        
        # 更新投诉状态为已处理
        complaint.status = '已处理'
        complaint.save()
        
        # 记录管理员操作日志
        ViolationRecord.objects.create(
            user=complaint.user,
            specialty=complaint.order.orderitem_set.first().specialty if complaint.order.orderitem_set.exists() else None,
            violation_type='投诉处理',
            process_result=f'投诉ID: {complaint_id}，处理意见: {opinion}'
        )
        
        return redirect('admin_complaints')
    
    return render(request, 'market/handle_complaint.html', {'complaint': complaint})

# 管理员查看所有产品（需要管理员权限）
@login_required
@user_passes_test(is_admin)
def admin_specialties(request):
    specialties = Specialty.objects.all()
    return render(request, 'market/admin_specialties.html', {'specialties': specialties})

# 管理员下架违规产品（需要管理员权限）
@login_required
@user_passes_test(is_admin)
def admin_toggle_specialty(request, specialty_id):
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    old_status = specialty.status
    new_status = '下架' if old_status == '上架' else '上架'
    specialty.status = new_status
    specialty.save()
    
    # 记录管理员操作日志
    ViolationRecord.objects.create(
        user=specialty.publisher,
        specialty=specialty,
        violation_type='产品状态变更',
        process_result=f'产品ID: {specialty_id}，状态从{old_status}变更为{new_status}'
    )
    
    return redirect('admin_specialties')

# 管理员查看所有用户（需要管理员权限）
@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all()
    return render(request, 'market/admin_users.html', {'users': users})

# 管理员冻结/解冻用户（需要管理员权限）
@login_required
@user_passes_test(is_admin)
def admin_toggle_user_status(request, user_id):
    # 防止管理员冻结自己
    if request.user.user_id == user_id:
        return redirect('admin_users')
    
    user = get_object_or_404(User, pk=user_id)
    old_status = user.status
    new_status = '冻结' if old_status == '正常' else '正常'
    user.status = new_status
    user.save()
    
    # 记录管理员操作日志
    ViolationRecord.objects.create(
        user=user,
        violation_type='用户状态变更',
        process_result=f'用户ID: {user_id}，状态从{old_status}变更为{new_status}'
    )
    
    return redirect('admin_users')


