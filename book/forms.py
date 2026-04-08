from django import forms
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
    class Meta:
        model = Member
        fields = ('user',
                  'name',
                  'gender',
                  'age',
                  'email',
                  'city', 
                  'phone_number',)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ( 'profile_pic',
                  'bio', 
                  'phone_number',
                  'email')

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
