from django.urls import path
from . import views

urlpatterns = [
    # API端点
    path('api/classifications/', views.classification_list, name='classification_list'),
    path('api/tags/', views.tag_list, name='tag_list'),
    path('api/things/', views.thing_list, name='thing_list'),
    path('api/thing/<int:thing_id>/', views.thing_detail, name='thing_detail'),
    path('api/thing/detail/', views.thing_detail_query, name='thing_detail_query'),
    path('api/notices/', views.notice_list_api, name='notice_list_api'),
    path('api/comments/', views.comment_list, name='comment_list'),
    path('api/comment/create/', views.create_comment, name='create_comment'),
    path('api/comment/like/', views.like_comment, name='like_comment'),
    path('api/comments/my/', views.list_my_comments, name='list_my_comments'),
    
    # 前端API路径兼容
    path('myapp/index/thing/list/', views.thing_list, name='thing_list_myapp'),
    path('myapp/index/thing/detail/', views.thing_detail_query, name='thing_detail_myapp'),
    path('myapp/index/classification/list/', views.classification_list, name='classification_list_myapp'),
    path('products/', views.products_view, name='products_view'),
    path('product/detail/', views.product_detail_view, name='product_detail_view'),
    
    # 用户认证
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # 首页和产品浏览
    path('', views.index, name='index'),
    path('specialty/<int:specialty_id>/', views.specialty_detail, name='specialty_detail'),
    
    # 用户产品管理
    path('publish/', views.publish_specialty, name='publish_specialty'),
    path('user/specialties/', views.user_specialties, name='user_specialties'),
    path('specialty/<int:specialty_id>/edit/', views.edit_specialty, name='edit_specialty'),
    path('specialty/<int:specialty_id>/toggle/', views.toggle_specialty_status, name='toggle_specialty_status'),
    path('specialty/<int:specialty_id>/delete/', views.delete_specialty, name='delete_specialty'),
    
    # 购物车和订单
    path('cart/add/<int:specialty_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.shopping_cart, name='shopping_cart'),
    path('cart/delete/<int:cart_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('user/orders/', views.user_orders, name='user_orders'),
    
    # 收藏功能
    path('collect/add/<int:specialty_id>/', views.collect_specialty, name='collect_specialty'),
    path('collect/<int:collect_id>/cancel/', views.cancel_collect, name='cancel_collect'),
    path('user/collections/', views.user_collections, name='user_collections'),
    
    # 投诉功能
    path('order/<int:order_id>/complaint/', views.submit_complaint, name='submit_complaint'),
    
    # 支付功能
    path('order/<int:order_id>/pay/', views.pay_order, name='pay_order'),
    
    # 管理员功能
    path('admin-complaints/', views.admin_complaints, name='admin_complaints'),
    path('admin-complaint/<int:complaint_id>/handle/', views.handle_complaint, name='handle_complaint'),
    path('admin-specialties/', views.admin_specialties, name='admin_specialties'),
    path('admin-specialty/<int:specialty_id>/toggle/', views.admin_toggle_specialty, name='admin_toggle_specialty'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-user/<int:user_id>/toggle/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
]