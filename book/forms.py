from django import forms
from django.contrib.auth.models import User, Group
from .models import Book,Publisher,Member,Profile,BorrowRecord
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib import admin
from django.urls import reverse
# from flatpickr import DatePickerInput, TimePickerInput, DateTimePickerInput
class DatePickerInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        kwargs.pop('options', None)
        super().__init__(*args, **kwargs)


class BookCreateEditForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('author',
                  'title',
                  'description',
                  'quantity', 
                  'category',
                  'publisher',
                  'floor_number',
                  "bookshelf_number")


class PubCreateEditForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name',
                  'city',
                  'contact',
                  )
        # fields="__all__"

class MemberCreateEditForm(forms.ModelForm):
    new_password = forms.CharField(
        label='新密码', required=False, widget=forms.PasswordInput,
        help_text='留空则不修改密码（需关联用户）',
    )
    new_password_confirm = forms.CharField(
        label='确认新密码', required=False, widget=forms.PasswordInput,
    )

    class Meta:
        model = Member
        fields = ('user',
                  'name',
                  'gender',
                  'age',
                  'email',
                  'city',
                  'phone_number',)

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('new_password')
        pw2 = cleaned_data.get('new_password_confirm')
        if pw and pw != pw2:
            self.add_error('new_password_confirm', '两次输入的密码不一致')
        if pw and not cleaned_data.get('user'):
            self.add_error('new_password', '未关联用户，无法修改密码')
        return cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ( 'profile_pic',
                  'bio', 
                  'phone_number',
                  'email')

class EmployeeCreateForm(forms.ModelForm):
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='确认密码', widget=forms.PasswordInput)
    is_staff = forms.BooleanField(label='员工权限', required=False, initial=True,
                                  help_text='允许登录管理后台')
    is_superuser = forms.BooleanField(label='超级管理员', required=False,
                                      help_text='拥有所有权限')
    groups = forms.ModelMultipleChoiceField(
        label='用户组', queryset=Group.objects.all(),
        required=False, widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        pw2 = cleaned_data.get('password_confirm')
        if pw and pw2 and pw != pw2:
            self.add_error('password_confirm', '两次输入的密码不一致')
        return cleaned_data


class EmployeeEditForm(forms.ModelForm):
    new_password = forms.CharField(
        label='新密码', required=False, widget=forms.PasswordInput,
        help_text='留空则不修改密码',
    )
    new_password_confirm = forms.CharField(
        label='确认新密码', required=False, widget=forms.PasswordInput,
    )
    is_staff = forms.BooleanField(label='员工权限', required=False, help_text='允许登录管理后台')
    is_active = forms.BooleanField(label='账号激活', required=False, help_text='取消勾选将禁止该用户登录')
    is_superuser = forms.BooleanField(label='超级管理员', required=False, help_text='拥有所有权限')
    groups = forms.ModelMultipleChoiceField(
        label='用户组', queryset=Group.objects.all(),
        required=False, widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': '用户名',
            'email': '邮箱',
            'first_name': '名',
            'last_name': '姓',
        }

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('new_password')
        pw2 = cleaned_data.get('new_password_confirm')
        if pw and pw != pw2:
            self.add_error('new_password_confirm', '两次输入的密码不一致')
        return cleaned_data


class BorrowRecordCreateForm(forms.ModelForm):
    borrower = forms.CharField(label='借阅者', required=False,
                    widget=forms.TextInput(attrs={'placeholder': '搜索会员...'}))
    
    book = forms.CharField(label='书籍名称', help_text='输入书名关键词')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(BorrowRecordCreateForm, self).__init__(*args, **kwargs)
        if self.user and not self.user.is_superuser:
            self.fields['borrower'].widget = forms.HiddenInput()
            self.fields['borrower'].required = False

    class Meta:
        model = BorrowRecord
        fields=['borrower','book','quantity','start_day','end_day']
        widgets = {
            'start_day': DatePickerInput(options = {  "dateFormat": "Y-m-d", }),
            'end_day': DatePickerInput(options = {  "dateFormat": "Y-m-d", }),
        }
        # widgets = {'start_day': forms.DateTimeInput(attrs={'class': 'datepicker'}),
        #            'end_day': forms.DateTimeInput(attrs={'class': 'datepicker'})}


        # widgets = {
        #     'start_day': DateTimePickerInput(format='%Y-%m-%d'),
        #     'end_day': DateTimePickerInput(format='%Y-%m-%d'),
        # }


# from  django.forms.widgets import SelectDateWidget

# class BorrowRecordCreateForm(forms.ModelForm):

#     def __init__(self, *args, **kwargs):
#         super(BorrowRecordCreateForm, self).__init__(*args, **kwargs)
#         #Change date field's widget here
#         self.fields['start_day'].widget = SelectDateWidget()
#         self.fields['end_day'].widget = SelectDateWidget()

#     class Meta:
#         model = BorrowRecord
#         fields=['borrower','book','quantity','start_day','end_day']
