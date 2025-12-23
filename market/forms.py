from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, Specialty, Origin
from datetime import date

class UserRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True, label='确认密码')
    
    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'role', 'phone', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': '用户名',
            'password': '密码',
            'role': '角色',
            'phone': '手机号',
            'email': '邮箱',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError('密码和确认密码不匹配')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True, label='用户名',
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=255, required=True, label='密码',
                                     widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        # 检查用户是否存在
        if username:
            try:
                user = User.objects.get(username=username)
                # 不在表单验证中检查冻结状态，让视图处理
                # 这样可以确保表单验证通过，但在视图中可以显示弹窗
                if not user.check_password(password):
                    raise forms.ValidationError('用户名或密码错误')
            except User.DoesNotExist:
                # 为了安全，不明确提示用户不存在
                raise forms.ValidationError('用户名或密码错误')
        
        return cleaned_data


class SpecialtyForm(forms.Form):
    # 产地信息
    origin_name = forms.CharField(max_length=100, required=True, label='产地名称',
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    province = forms.CharField(max_length=50, required=True, label='省份',
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=50, required=True, label='城市',
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    district = forms.CharField(max_length=50, required=True, label='区县',
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # 产品信息
    category = forms.CharField(max_length=50, required=True, label='产品类别',
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(max_length=100, required=True, label='产品名称',
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, label='产品图片',
                            widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}))
    description = forms.CharField(required=False, label='产品描述',
                                 widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label='销售价格',
                              widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}))
    sale_start_time = forms.DateField(required=True, label='销售开始时间',
                                     widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    sale_end_time = forms.DateField(required=True, label='销售结束时间',
                                   widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    
    def clean(self):
        cleaned_data = super().clean()
        sale_start_time = cleaned_data.get('sale_start_time')
        sale_end_time = cleaned_data.get('sale_end_time')
        price = cleaned_data.get('price')
        image = cleaned_data.get('image')
        
        # 验证价格
        if price is not None and price <= 0:
            raise forms.ValidationError('价格必须大于0')
        
        # 验证时间
        if sale_start_time and sale_end_time:
            if sale_start_time < date.today():
                raise forms.ValidationError('销售开始时间不能早于今天')
            if sale_end_time < sale_start_time:
                raise forms.ValidationError('销售结束时间不能早于开始时间')
        
        # 验证图片大小（可选）
        if image and image.size > 2 * 1024 * 1024:  # 2MB
            raise forms.ValidationError('图片大小不能超过2MB')
        
        return cleaned_data


class SpecialtyEditForm(forms.Form):
    # 产品编辑表单，基于SpecialtyForm但允许不修改图片
    # 产地信息
    origin_name = forms.CharField(max_length=100, required=True, label='产地名称',
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    province = forms.CharField(max_length=50, required=True, label='省份',
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=50, required=True, label='城市',
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    district = forms.CharField(max_length=50, required=True, label='区县',
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # 产品信息
    category = forms.CharField(max_length=50, required=True, label='产品类别',
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(max_length=100, required=True, label='产品名称',
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, label='产品图片（留空则不修改）',
                            widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}))
    description = forms.CharField(required=False, label='产品描述',
                                 widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label='销售价格',
                              widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}))
    sale_start_time = forms.DateField(required=True, label='销售开始时间',
                                     widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    sale_end_time = forms.DateField(required=True, label='销售结束时间',
                                   widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    status = forms.ChoiceField(choices=[('上架', '上架'), ('下架', '下架')], 
                              required=True, label='产品状态',
                              widget=forms.Select(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        sale_start_time = cleaned_data.get('sale_start_time')
        sale_end_time = cleaned_data.get('sale_end_time')
        price = cleaned_data.get('price')
        image = cleaned_data.get('image')
        
        # 验证价格
        if price is not None and price <= 0:
            raise forms.ValidationError('价格必须大于0')
        
        # 验证时间
        if sale_start_time and sale_end_time:
            if sale_end_time < sale_start_time:
                raise forms.ValidationError('销售结束时间不能早于开始时间')
        
        # 验证图片大小（可选）
        if image and image.size > 2 * 1024 * 1024:  # 2MB
            raise forms.ValidationError('图片大小不能超过2MB')
        
        return cleaned_data


class OrderForm(forms.Form):
    address = forms.CharField(max_length=255, required=True, label='收货地址',
                            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    phone = forms.CharField(max_length=20, required=True, label='联系电话',
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    receiver = forms.CharField(max_length=50, required=True, label='收货人',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # 简单的手机号验证
        if not phone.isdigit() or len(phone) < 10:
            raise forms.ValidationError('请输入有效的手机号')
        return phone