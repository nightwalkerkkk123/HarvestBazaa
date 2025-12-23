from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class Origin(models.Model):
    origin_id = models.AutoField(primary_key=True)
    origin_name = models.CharField(max_length=100, blank=False, null=False)
    province = models.CharField(max_length=50, blank=False, null=False)
    city = models.CharField(max_length=50, blank=False, null=False)
    district = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'origins'
        managed = False
        unique_together = ('province', 'city', 'district')

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名是必须的')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', '管理员')
        extra_fields.setdefault('status', '正常')
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, blank=False, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    role = models.CharField(max_length=10, choices=[('管理员', '管理员'), ('普通用户', '普通用户')], default='普通用户')
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('正常', '正常'), ('冻结', '冻结')], default='正常')
    register_time = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    @property
    def is_staff(self):
        return self.role == '管理员'
    
    @property
    def is_active(self):
        return self.status == '正常'
    
    class Meta:
        db_table = 'users'
        managed = False

class Specialty(models.Model):
    specialty_id = models.AutoField(primary_key=True)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, db_column='publisher_id')
    origin = models.ForeignKey(Origin, on_delete=models.RESTRICT, db_column='origin_id')
    category = models.CharField(max_length=50, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    sale_start_time = models.DateField(blank=False, null=False)
    sale_end_time = models.DateField(blank=False, null=False)
    status = models.CharField(max_length=10, choices=[('上架', '上架'), ('下架', '下架')], default='上架')
    create_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, default='default-product.jpg')
    
    class Meta:
        db_table = 'specialties'
        managed = False

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    status = models.CharField(max_length=10, choices=[('待支付', '待支付'), ('已支付', '已支付'), ('已完成', '已完成'), ('已取消', '已取消')], default='待支付')
    order_time = models.DateTimeField(auto_now_add=True)
    pay_time = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'orders'
        managed = False

class OrderItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, db_column='specialty_id')
    quantity = models.IntegerField(default=1, blank=False, null=False)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    
    class Meta:
        db_table = 'order_items'
        managed = False

class ShoppingCart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, db_column='specialty_id')
    quantity = models.IntegerField(default=1, blank=False, null=False)
    add_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shopping_carts'
        managed = False

class Collection(models.Model):
    collect_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, db_column='specialty_id')
    collect_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'collections'
        managed = False

class Complaint(models.Model):
    complaint_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    complaint_type = models.CharField(max_length=50, blank=False, null=False)
    reason = models.TextField(blank=False, null=False)
    status = models.CharField(max_length=10, choices=[('待处理', '待处理'), ('已处理', '已处理')], default='待处理')
    complaint_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'complaints'
        managed = False

class ComplaintHandle(models.Model):
    handle_id = models.AutoField(primary_key=True)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, db_column='complaint_id')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, db_column='admin_id')
    opinion = models.TextField(blank=False, null=False)
    handle_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'complaint_handles'
        managed = False

class ViolationRecord(models.Model):
    violation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True, db_column='specialty_id')
    violation_type = models.CharField(max_length=100, blank=False, null=False)
    violation_time = models.DateTimeField(auto_now_add=True)
    process_result = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'violation_records'
        managed = False
