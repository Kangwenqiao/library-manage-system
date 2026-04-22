import os
import json
import re

from django.db.models.functions import ExtractMonth,ExtractWeek,TruncMonth,TruncWeek
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import  reverse_lazy,reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView,DetailView,DeleteView,View,TemplateView
from django.views.generic.edit import CreateView,UpdateView
from django.core.paginator import Paginator
from django.db.models import Q,Sum
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from .models import Book,Category,Publisher,UserActivity,Profile,Member,BorrowRecord
from django.apps import apps
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from .forms import BookCreateEditForm,PubCreateEditForm,MemberCreateEditForm,ProfileForm,BorrowRecordCreateForm,EmployeeCreateForm,EmployeeEditForm

# from .utils import get_n_days_ago,create_clean_dir,change_col_format
from util.useful import get_n_days_ago,create_clean_dir,change_col_format
from .groups_permissions import check_user_group,user_groups,check_superuser,SuperUserRequiredMixin,allowed_groups,AdminRequiredMixin,BorrowerRequiredMixin
from .custom_filter import get_item
from datetime import date,timedelta,datetime

from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from comment.models import Comment
from comment.forms import CommentForm
from notifications.signals import notify
from .notification import send_notification, send_notification_to_user
import logging

logger = logging.getLogger(__name__)



TODAY=get_n_days_ago(0,"%Y%m%d")
PAGINATOR_NUMBER = 5
allowed_models = ['Category','Publisher','Book','Member','UserActivity','BorrowRecord']



# HomePage

class HomeView(LoginRequiredMixin,TemplateView):
    login_url = 'login'
    template_name = "index.html"
    context={}

    def get(self,request, *args, **kwargs):
        if request.user.is_superuser:
            # 管理端数据
            book_count = Book.objects.aggregate(Sum('quantity'))['quantity__sum']
            data_count = {"book":book_count,
                        "member":Member.objects.all().count(),
                        "category":Category.objects.all().count(),
                        "publisher":Publisher.objects.all().count(),}

            user_activities= UserActivity.objects.order_by("-created_at")[:5]
            user_avatar = {}
            for e in user_activities:
                try:
                    user_avatar[e.created_by] = Profile.objects.get(user__username=e.created_by).profile_pic.url
                except:
                    user_avatar[e.created_by] = "/static/assets/img/theme/team-1.jpg"
            
            short_inventory =Book.objects.order_by('quantity')[:5]
            
            current_week = date.today().isocalendar()[1]
            new_members = Member.objects.order_by('-created_at')[:5]
            new_members_thisweek = Member.objects.filter(created_at__week=current_week).count()
            lent_books_thisweek = BorrowRecord.objects.filter(created_at__week=current_week).count()

            books_return_thisweek = BorrowRecord.objects.filter(end_day__week=current_week)
            number_books_return_thisweek = books_return_thisweek.count()
            new_closed_records = BorrowRecord.objects.filter(open_or_close=1).order_by('-closed_at')[:5]

            self.context['data_count']=data_count
            self.context['recent_user_activities']=user_activities
            self.context['user_avatar']=user_avatar
            self.context['short_inventory']=short_inventory
            self.context['new_members']=new_members
            self.context['new_members_thisweek']=new_members_thisweek
            self.context['lent_books_thisweek']=lent_books_thisweek
            self.context['books_return_thisweek']=books_return_thisweek
            self.context['number_books_return_thisweek']=number_books_return_thisweek
            self.context['new_closed_records']=new_closed_records
        else:
            # 借阅端数据
            my_records = BorrowRecord.objects.filter(user=request.user).order_by("-created_at")
            self.context['my_records'] = my_records[:5]
            self.context['total_borrowed'] = my_records.count()
            self.context['on_loan'] = my_records.filter(open_or_close=0).count()
            
        return render(request, self.template_name, self.context)

# Global Serch
@login_required(login_url='login')
def global_serach(request):
    search_value = request.POST.get('global_search')
    if search_value =='':
        return HttpResponseRedirect("/")

    r_category = Category.objects.filter(Q(name__icontains=search_value))
    r_publisher = Publisher.objects.filter(Q(name__icontains=search_value)|Q(contact__icontains=search_value))
    r_book = Book.objects.filter(Q(author__icontains=search_value)|Q(title__icontains=search_value))
    r_member = Member.objects.filter(Q(name__icontains=search_value)|Q(card_number__icontains=search_value)|Q(phone_number__icontains=search_value))
    r_borrow = BorrowRecord.objects.filter(Q(borrower__icontains=search_value)|Q(borrower_card__icontains=search_value)|Q(book__icontains=search_value))

   
    context={
        'categories':r_category,
        'publishers':r_publisher,
        'books':r_book,
        'members':r_member,
        'records':r_borrow,
    }

    return render(request, 'book/global_search.html',context=context)


# Chart
class ChartView(LoginRequiredMixin,TemplateView):
    template_name = "book/charts.html"
    login_url = 'login'
    context={}

    def get(self,request, *args, **kwargs):

        top_5_book= Book.objects.order_by('-quantity')[:5].values_list('title','quantity')
        top_5_book_titles = [b[0] for b in top_5_book ]
        top_5_book__quantities = [b[1] for b in top_5_book ]
        # print(top_5_book_titles,top_5_book__quantities)

        top_borrow = Book.objects.order_by('-total_borrow_times')[:5].values_list('title','total_borrow_times')
        top_borrow_titles = [b[0] for b in top_borrow ]
        top_borrow_times = [b[1] for b in top_borrow ]

        r_open = BorrowRecord.objects.filter(open_or_close=0).count()
        r_close = BorrowRecord.objects.filter(open_or_close=1).count()
        
        m = Member.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(c=Count('id'))
        months_member = [e['month'].strftime("%m/%Y") for e  in m]
        count_monthly_member= [e['c'] for e in m] 

       
        self.context['top_5_book_titles']=top_5_book_titles
        self.context['top_5_book__quantities']=top_5_book__quantities
        self.context['top_borrow_titles']=top_borrow_titles
        self.context['top_borrow_times']=top_borrow_times
        self.context['r_open']=r_open
        self.context['r_close']=r_close
        self.context['months_member']=months_member
        self.context['count_monthly_member']=count_monthly_member
       

        return render(request, self.template_name, self.context)

# Book
class BookListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    model=Book
    context_object_name = 'books'
    template_name = 'book/book_list.html'
    search_value=""
    order_field="-updated_at"

    def get_queryset(self):
        search =self.request.GET.get("search") 
        order_by=self.request.GET.get("orderby")

        if order_by:
            all_books = Book.objects.all().order_by(order_by)
            self.order_field=order_by
        else:
            all_books = Book.objects.all().order_by(self.order_field)

        if search:
            all_books = all_books.filter(
                Q(title__icontains=search)|Q(author__icontains=search)
            )
            self.search_value=search
        self.count_total = all_books.count()
        paginator = Paginator(all_books, PAGINATOR_NUMBER)
        page = self.request.GET.get('page')
        books = paginator.get_page(page)
        return books

    def get_context_data(self, *args, **kwargs):
        context = super(BookListView, self).get_context_data(*args, **kwargs)
        context['count_total'] = self.count_total
        context['search'] = self.search_value
        context['orderby'] = self.order_field
        context['objects'] = self.get_queryset()
        return context

class BookDetailView(LoginRequiredMixin,DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'book/book_detail.html'
    login_url = 'login'
    comment_form = CommentForm()
    
    # def get_object(self, queryset=None):
    #     obj = super(BookDetailView, self).get_object(queryset=queryset)
    #     return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_book_name = self.get_object().title
        logger.info(f'Book  <<{current_book_name}>> retrieved from db')
        comments = Comment.objects.filter(book=self.get_object().id)
        related_records = BorrowRecord.objects.filter(book=current_book_name)
        context['related_records'] = related_records
        context['comments'] = comments
        context['comment_form'] = self.comment_form
        return context

class BookCreateView(AdminRequiredMixin,CreateView):
    model=Book
    login_url = 'login'
    form_class=BookCreateEditForm    
    template_name='book/book_create.html'

    def post(self,request, *args, **kwargs):
        super(BookCreateView,self).post(request)
        new_book_name = request.POST['title']
        messages.success(request, f"New Book << {new_book_name} >> Added")
        UserActivity.objects.create(created_by=self.request.user.username,
                                    target_model=self.model.__name__,
                                    detail =f"Create {self.model.__name__} << {new_book_name} >>")
        return redirect('book_list')

class BookUpdateView(AdminRequiredMixin,UpdateView):
    model = Book
    login_url = 'login'
    form_class=BookCreateEditForm
    template_name = 'book/book_update.html'

    def post(self, request, *args, **kwargs):
        current_book = self.get_object()
        current_book.updated_by=self.request.user.username
        current_book.save(update_fields=['updated_by'])
        UserActivity.objects.create(created_by=self.request.user.username,
            operation_type="warning",
            target_model=self.model.__name__,
            detail =f"Update {self.model.__name__} << {current_book.title} >>")
        return super(BookUpdateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
      title=form.cleaned_data['title']      
      messages.warning(self.request, f"Update << {title} >> success")
      return super().form_valid(form)

class BookDeleteView(AdminRequiredMixin,View):
    login_url = 'login'
    def get(self,request,*args,**kwargs):
        book_pk=kwargs["pk"]
        delete_book=Book.objects.get(pk=book_pk)
        model_name = delete_book.__class__.__name__
        messages.error(request, f"Book << {delete_book.title} >> Removed")
        delete_book.delete()
        UserActivity.objects.create(created_by=self.request.user.username,
            operation_type="danger",
            target_model=model_name,
            detail =f"Delete {model_name} << {delete_book.title} >>")
        return HttpResponseRedirect(reverse("book_list"))

# Categorty

class CategoryListView(AdminRequiredMixin,ListView):
    login_url = 'login'
    model=Category
    context_object_name = 'categories'
    template_name = 'book/category_list.html'
    count_total = 0
    search_value = ''
    order_field="-created_at"


    def get_queryset(self):
        search =self.request.GET.get("search")  
        order_by=self.request.GET.get("orderby")
        if order_by:
            all_categories = Category.objects.all().order_by(order_by)
            self.order_field=order_by
        else:
            all_categories = Category.objects.all().order_by(self.order_field)
        if search:
            all_categories = all_categories.filter(
                Q(name__icontains=search)  
            )
            self.search_value=search

        self.count_total = all_categories.count()
        paginator = Paginator(all_categories, PAGINATOR_NUMBER)
        page = self.request.GET.get('page')
        categories = paginator.get_page(page)
        return categories

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryListView, self).get_context_data(*args, **kwargs)
        context['count_total'] = self.count_total
        context['search'] = self.search_value
        context['orderby'] = self.order_field
        context['objects'] = self.get_queryset()
        return context

class CategoryCreateView(AdminRequiredMixin,CreateView):
    login_url = 'login'
    model=Category
    fields=['name']
    template_name='book/category_create.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        new_cat = form.save(commit=False)
        new_cat.save()
        send_notification(self.request.user,new_cat,verb=f'Add New Category << {new_cat.name} >>')
        logger.info(f'{self.request.user} created Category {new_cat.name}')
        UserActivity.objects.create(created_by=self.request.user.username,
                                    target_model=self.model.__name__,
                                    detail =f"Create {self.model.__name__} << {new_cat.name} >>")
        return super(CategoryCreateView, self).form_valid(form)



class CategoryDeleteView(AdminRequiredMixin,View):
    login_url = 'login'

    def get(self,request,*args,**kwargs):
        cat_pk=kwargs["pk"]
        delete_cat=Category.objects.get(pk=cat_pk)
        model_name = delete_cat.__class__.__name__
        messages.error(request, f"Category << {delete_cat.name} >> Removed")
        delete_cat.delete()
        send_notification(self.request.user,delete_cat,verb=f'Delete Category << {delete_cat.name} >>')
        UserActivity.objects.create(created_by=self.request.user.username,
                            operation_type="danger",
                            target_model=model_name,
                            detail =f"Delete {model_name} << {delete_cat.name} >>")

        logger.info(f'{self.request.user} delete Category {delete_cat.name}')

        return HttpResponseRedirect(reverse("category_list"))


# Publisher 

class PublisherListView(AdminRequiredMixin,ListView):
    login_url = 'login'
    model=Publisher
    context_object_name = 'publishers'
    template_name = 'book/publisher_list.html'
    count_total = 0
    search_value = ''
    order_field="-created_at"

    def get_queryset(self):
        search =self.request.GET.get("search")  
        order_by=self.request.GET.get("orderby")
        if order_by:
            all_publishers = Publisher.objects.all().order_by(order_by)
            self.order_field=order_by
        else:
            all_publishers = Publisher.objects.all().order_by(self.order_field)
        if search:
            all_publishers = all_publishers.filter(
                Q(name__icontains=search) | Q(city__icontains=search) | Q(contact__icontains=search)
            )
        else:
            search = ''
        self.search_value=search
        self.count_total = all_publishers.count()
        paginator = Paginator(all_publishers, PAGINATOR_NUMBER)
        page = self.request.GET.get('page')
        publishers = paginator.get_page(page)
        return publishers

    def get_context_data(self, *args, **kwargs):
        context = super(PublisherListView, self).get_context_data(*args, **kwargs)
        context['count_total'] = self.count_total
        context['search'] = self.search_value
        context['orderby'] = self.order_field  
        context['objects'] = self.get_queryset()      
        return context

class PublisherCreateView(AdminRequiredMixin,CreateView):
    model=Publisher
    login_url = 'login'
    form_class=PubCreateEditForm
    template_name='book/publisher_create.html'
    success_url = reverse_lazy('publisher_list')


    def form_valid(self,form):
        new_pub = form.save(commit=False)
        new_pub.save()
        messages.success(self.request, f"New Publisher << {new_pub.name} >> Added")
        send_notification(self.request.user,new_pub,verb=f'Add New Publisher << {new_pub.name} >>')
        logger.info(f'{self.request.user} created Publisher {new_pub.name}')

        UserActivity.objects.create(created_by=self.request.user.username,
                                    target_model=self.model.__name__,
                                    detail =f"Create {self.model.__name__} << {new_pub.name} >>")
        return super(PublisherCreateView, self).form_valid(form)

    # def post(self,request, *args, **kwargs):
    #     super(PublisherCreateView,self).post(request)
    #     new_publisher_name = request.POST['name']
    #     messages.success(request, f"New Publisher << {new_publisher_name} >> Added")
    #     UserActivity.objects.create(created_by=self.request.user.username,
    #                                 target_model=self.model.__name__,
    #                                 detail =f"Create {self.model.__name__} << {new_publisher_name} >>")
    #     return redirect('publisher_list')

class PublisherUpdateView(AdminRequiredMixin,UpdateView):
    model=Publisher
    login_url = 'login'
    form_class=PubCreateEditForm
    template_name = 'book/publisher_update.html'

    def post(self, request, *args, **kwargs):
        current_pub = self.get_object()
        current_pub.updated_by=self.request.user.username
        current_pub.save(update_fields=['updated_by'])
        UserActivity.objects.create(created_by=self.request.user.username,
                                    operation_type="warning",
                                    target_model=self.model.__name__,
                                    detail =f"Update {self.model.__name__} << {current_pub.name} >>")
        return super(PublisherUpdateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        title=form.cleaned_data['name']      
        messages.warning(self.request, f"Update << {title} >> success")
        return super().form_valid(form)

class PublisherDeleteView(AdminRequiredMixin,View):
    login_url = 'login'

    def get(self,request,*args,**kwargs):
        pub_pk=kwargs["pk"]
        delete_pub=Publisher.objects.get(pk=pub_pk)
        model_name = delete_pub.__class__.__name__
        messages.error(request, f"Publisher << {delete_pub.name} >> Removed")
        delete_pub.delete()
        send_notification(self.request.user,delete_pub,verb=f'Delete Publisher << {delete_pub.name} >>')
        logger.info(f'{self.request.user} delete Publisher {delete_pub.name}')
        UserActivity.objects.create(created_by=self.request.user.username,
                    operation_type="danger",
                    target_model=model_name,
                    detail =f"Delete {model_name} << {delete_pub.name} >>")
        return HttpResponseRedirect(reverse("publisher_list"))


# User Logs  
# @method_decorator(user_passes_test(lambda u: u.has_perm("book.view_useractivity")), name='dispatch')
@method_decorator(allowed_groups(group_name=['logs']), name='dispatch')
class ActivityListView(AdminRequiredMixin,ListView):

    login_url = 'login'
    model= UserActivity
    context_object_name = 'activities'
    template_name = 'book/user_activity_list.html'
    count_total = 0
    search_value=''
    created_by=''
    order_field="-created_at"

    # def dispatch(self, *args, **kwargs):
    #     return super(ActivityListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        data = self.request.GET.copy()
        search =self.request.GET.get("search")
        filter_user=self.request.GET.get("created_by") 

        all_activities = UserActivity.objects.all()

        if filter_user:
            self.created_by = filter_user
            all_activities = all_activities.filter(created_by=self.created_by)

        if search:
            self.search_value = search
            all_activities = all_activities.filter(Q(target_model__icontains=search))

        self.search_value=search
        self.count_total = all_activities.count()
        paginator = Paginator(all_activities,PAGINATOR_NUMBER)
        page = self.request.GET.get('page')
        try:
            response = paginator.get_page(page)
        except PageNotAnInteger:
            response = paginator.get_page(1)
        except EmptyPage:
            response = paginator.get_page(paginator.num_pages)
        return response

    
    def get_context_data(self, *args, **kwargs):
        context = super(ActivityListView, self).get_context_data(*args, **kwargs)
        context['count_total'] = self.count_total
        context['search'] = self.search_value
        context['user_list'] = list(User.objects.values_list('username', flat=True))
        context['created_by'] = self.created_by
        return context


# @method_decorator(user_passes_test(lambda u: u.has_perm("book.delete_useractivity")), name='dispatch')
@method_decorator(allowed_groups(group_name=['logs']), name='dispatch')
class ActivityDeleteView(AdminRequiredMixin,View):

    login_url = 'login'

    def get(self,request,*args,**kwargs):
        
        log_pk=kwargs["pk"]
        delete_log=UserActivity.objects.get(pk=log_pk)
        messages.error(request, f"Activity Removed")
        delete_log.delete()

        return HttpResponseRedirect(reverse("user_activity_list"))


# Membership
class MemberListView(AdminRequiredMixin,ListView):
    login_url = 'login'
    model= Member
    context_object_name = 'members'
    template_name = 'book/member_list.html'
    count_total = 0
    search_value = ''
    order_field="-updated_at"

    def get_queryset(self):
        search =self.request.GET.get("search")  
        order_by=self.request.GET.get("orderby")
        if order_by:
            all_members = Member.objects.all().order_by(order_by)
            self.order_field=order_by
        else:
            all_members = Member.objects.all().order_by(self.order_field)
        if search:
            all_members = all_members.filter(
                Q(name__icontains=search) |  Q(card_number__icontains=search)
            )
        else:
            search = ''
        self.search_value=search
        self.count_total = all_members.count()
        paginator = Paginator(all_members, PAGINATOR_NUMBER)
        page = self.request.GET.get('page')
        members = paginator.get_page(page)
        return members

    def get_context_data(self, *args, **kwargs):
        context = super(MemberListView, self).get_context_data(*args, **kwargs)
        context['count_total'] = self.count_total
        context['search'] = self.search_value
        context['orderby'] = self.order_field
        context['objects'] = self.get_queryset()
        return context

class MemberCreateView(AdminRequiredMixin,CreateView):
    model=Member
    login_url = 'login'
    form_class=MemberCreateEditForm
    template_name='book/member_create.html'

    def post(self,request, *args, **kwargs):
        super(MemberCreateView,self).post(request)
        new_member_name = request.POST['name']
        messages.success(request, f"New Member << {new_member_name} >> Added")
        UserActivity.objects.create(created_by=self.request.user.username,
                                    target_model=self.model.__name__,
                                    detail =f"Create {self.model.__name__} << {new_member_name} >>")
        return redirect('member_list')

    def form_valid(self, form):
        self.object = form.save()
        self.object.created_by = self.request.user.username
        self.object.save(update_fields=['created_by'])
        send_notification(self.request.user,self.object,f'Add new memeber {self.object.name}')
    
        return HttpResponseRedirect(self.get_success_url())


    # def form_valid(self, form):
    #     response = super(CourseCreate, self).form_valid(form)
    #     # do something with self.object
    #     return response

class MemberUpdateView(AdminRequiredMixin,UpdateView):
    model = Member
    login_url = 'login'
    form_class=MemberCreateEditForm
    template_name = 'book/member_update.html'

    def _can_change_password(self):
        member = self.get_object()
        user = self.request.user
        return user.is_superuser or (member.user and member.user == user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self._can_change_password():
            del form.fields['new_password']
            del form.fields['new_password_confirm']
        return form

    def post(self, request, *args, **kwargs):
        current_member = self.get_object()
        current_member.updated_by=self.request.user.username
        current_member.save(update_fields=['updated_by'])
        UserActivity.objects.create(created_by=self.request.user.username,
            operation_type="warning",
            target_model=self.model.__name__,
            detail =f"Update {self.model.__name__} << {current_member.name} >>")
        return super(MemberUpdateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        new_pw = form.cleaned_data.get('new_password')
        if new_pw and self._can_change_password():
            member_user = form.cleaned_data.get('user') or self.get_object().user
            if member_user:
                member_user.set_password(new_pw)
                member_user.save(update_fields=['password'])
        member_name=form.cleaned_data['name']
        messages.warning(self.request, f"更新 << {member_name} >> 成功")
        return super().form_valid(form)

class MemberDeleteView(AdminRequiredMixin,View):
    login_url = 'login'

    def get(self,request,*args,**kwargs):
        member_pk=kwargs["pk"]
        delete_member=Member.objects.get(pk=member_pk)
        model_name = delete_member.__class__.__name__
        messages.error(request, f"Member << {delete_member.name} >> Removed")
        delete_member.delete()
        send_notification(self.request.user,delete_member,f'Delete member {delete_member.name} ')


        UserActivity.objects.create(created_by=self.request.user.username,
                    operation_type="danger",
                    target_model=model_name,
                    detail =f"Delete {model_name} << {delete_member.name} >>")
        return HttpResponseRedirect(reverse("member_list"))

class MemberDetailView(AdminRequiredMixin,DetailView):
    model = Member
    context_object_name = 'member'
    template_name = 'book/member_detail.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_member_name = self.get_object().name
        related_records = BorrowRecord.objects.filter(borrower=current_member_name)
        context['related_records'] = related_records
        context["card_number"] = str(self.get_object().card_id)[:8]
        return context


# Profile View

class ProfileDetailView(LoginRequiredMixin,DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'profile/profile_detail.html'
    login_url = 'login'


    def get_context_data(self, *args, **kwargs):
        current_user= get_object_or_404(Profile,pk=self.kwargs['pk'])
        # current_user= Profile.get(pk=kwargs['pk'])
        context = super(ProfileDetailView, self).get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        return context

class ProfileCreateView(LoginRequiredMixin,CreateView):
    model = Profile
    template_name = 'profile/profile_create.html'
    login_url = 'login'
    form_class= ProfileForm

    def form_valid(self,form) -> HttpResponse:
        form.instance.user = self.request.user
        return super().form_valid(form)

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    model = Profile
    login_url = 'login'
    form_class=ProfileForm
    template_name = 'profile/profile_update.html'

# Borrow Records 

class BorrowRecordCreateView(LoginRequiredMixin,CreateView):
    model = BorrowRecord
    template_name = 'borrow_records/create.html'
    form_class=BorrowRecordCreateForm
    login_url = 'login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_form(self):
        form = super().get_form()
        # 如果从图书列表点击“借阅”，预填书名
        book_title = self.request.GET.get('book')
        if book_title:
            form.fields['book'].initial = book_title
        return form

    def form_valid(self, form):
        # 自动关联用户
        if not self.request.user.is_superuser:
            form.instance.user = self.request.user
            try:
                member = self.request.user.member
                form.instance.borrower = member.name
                form.instance.borrower_card = member.card_number
                form.instance.borrower_email = member.email
                form.instance.borrower_phone_number = member.phone_number
            except:
                # 如果没有关联 Member，则使用用户名
                form.instance.borrower = self.request.user.username
        else:
            # 管理员手动选择
            selected_member = get_object_or_404(Member, name=form.cleaned_data['borrower'])
            form.instance.user = selected_member.user
            form.instance.borrower_card = selected_member.card_number
            form.instance.borrower_email = selected_member.email
            form.instance.borrower_phone_number = selected_member.phone_number

        selected_book = Book.objects.get(title=form.cleaned_data['book'])
        form.instance.book_link = selected_book
        form.instance.book_title = selected_book.title
        form.instance.created_by = self.request.user.username
        form.instance.start_day = form.cleaned_data['start_day']
        form.instance.end_day = form.cleaned_data['end_day']

        borrower_name = form.instance.borrower
        book_name = selected_book.title

        if self.request.user.is_staff:
            # 管理员直接通过，扣库存
            form.instance.open_or_close = 0
            form.save()
            selected_book.status = 0
            selected_book.total_borrow_times += 1
            selected_book.quantity -= int(form.cleaned_data['quantity'])
            selected_book.save()
            messages.success(self.request, f"'{borrower_name}' 已借阅《{book_name}》")
            UserActivity.objects.create(created_by=self.request.user.username,
                                        target_model=self.model.__name__,
                                        detail=f"'{borrower_name}' borrowed <<{book_name}>>")
        else:
            # 读者提交申请，待审批，不扣库存
            form.instance.open_or_close = 3
            form.save()
            send_notification(
                self.request.user, form.instance,
                verb=f"申请借阅《{book_name}》",
            )
            messages.success(self.request, "借阅申请已提交，请等待管理员审批")
            UserActivity.objects.create(created_by=self.request.user.username,
                                        target_model=self.model.__name__,
                                        detail=f"'{borrower_name}' 申请借阅《{book_name}》")

        return super(BorrowRecordCreateView, self).form_valid(form)

 
    # def post(self,request, *args, **kwargs):

    #     return redirect('record_list')



@login_required(login_url='login')
def auto_member(request):
    if request.is_ajax():
        query = request.GET.get("term", "")
        member_names = Member.objects.filter(name__icontains=query)
        results = []
        for m in member_names:
            results.append(m.name)
        data = json.dumps(results)
    mimetype = "application/json"
    return HttpResponse(data, mimetype)

@login_required(login_url='login')
def auto_book(request):
    if request.is_ajax():
        query = request.GET.get("term", "")
        book_names = Book.objects.filter(title__icontains=query)
        results = [b.title for b in book_names]
        data = json.dumps(results)
    mimetype = "application/json"
    return HttpResponse(data, mimetype)

class BorrowRecordDetailView(LoginRequiredMixin,DetailView):
    model = BorrowRecord
    context_object_name = 'record'
    template_name = 'borrow_records/detail.html'
    login_url = 'login'   

    # def get_queryset(self):
    #     return BorrowRecord.objects.filter(pk=self.kwargs['pk'])

    # Not recommanded
    def get_context_data(self, **kwargs):
        context = super(BorrowRecordDetailView, self).get_context_data(**kwargs)
        context['related_member'] = Member.objects.filter(name=self.get_object().borrower).first()
        return context

class BorrowRecordListView(LoginRequiredMixin,ListView):
    model = BorrowRecord
    template_name = 'borrow_records/list.html'
    login_url = 'login'
    context_object_name = 'records'
    count_total = 0
    search_value = ''
    order_field="-closed_at"

    def get_queryset(self):
        search =self.request.GET.get("search")  
        order_by=self.request.GET.get("orderby")
        
        if self.request.user.is_staff:
            all_records = BorrowRecord.objects.all()
        else:
            all_records = BorrowRecord.objects.filter(user=self.request.user)

        if order_by:
            all_records = all_records.order_by(order_by)
            self.order_field=order_by
        else:
            all_records = all_records.order_by(self.order_field)

        if search:
            all_records = all_records.filter(
                Q(borrower__icontains=search) | Q(book_title__icontains=search) | Q(borrower_card__icontains=search)
            )
            self.search_value=search
        else:
            self.search_value = ''

        self.count_total = all_records.count()
        paginator = Paginator(all_records, PAGINATOR_NUMBER)
        page = self.request.GET.get('page')
        records = paginator.get_page(page)
        return records

    def get_context_data(self, *args, **kwargs):
        context = super(BorrowRecordListView, self).get_context_data(*args, **kwargs)
        context['count_total'] = self.count_total
        context['search'] = self.search_value
        context['orderby'] = self.order_field
        context['objects'] = self.get_queryset()
        return context

class BorrowRecordDeleteView(AdminRequiredMixin,View):
    login_url = 'login'

    def get(self,request,*args,**kwargs):
        record_pk=kwargs["pk"]
        delete_record=BorrowRecord.objects.get(pk=record_pk)
        model_name = delete_record.__class__.__name__
        messages.error(request, f"Record {delete_record.borrower} => {delete_record.book_title} Removed")
        delete_record.delete()
        UserActivity.objects.create(created_by=self.request.user.username,
                    operation_type="danger",
                    target_model=model_name,
                    detail =f"Delete {model_name} {delete_record.borrower}")
        return HttpResponseRedirect(reverse("record_list"))

class BorrowRecordClose(AdminRequiredMixin,View):
    def get(self, request, *args, **kwargs):

        close_record = get_object_or_404(BorrowRecord, pk=self.kwargs['pk'])
        if close_record.open_or_close == 1:
            return HttpResponseRedirect(reverse("record_list"))

        close_record.closed_by = self.request.user.username
        close_record.final_status = close_record.return_status
        close_record.delay_days = close_record.get_delay_number_days
        close_record.open_or_close = 1
        close_record.save()

        borrowed_book = close_record.book_link
        if borrowed_book:
            borrowed_book.quantity += 1
            count_record_same_book = BorrowRecord.objects.filter(book_link=borrowed_book, open_or_close=0).count()
            if count_record_same_book == 0:
                borrowed_book.status = 1
            borrowed_book.save()

        model_name = close_record.__class__.__name__
        UserActivity.objects.create(created_by=self.request.user.username,
                    operation_type="info",
                    target_model=model_name,
                    detail =f"Close {model_name} '{close_record.borrower}'=>{close_record.book_title}")

        # 通知借阅者：还书已确认
        if close_record.user:
            send_notification_to_user(
                request.user, close_record.user, close_record,
                verb=f"已确认归还《{close_record.book_title}》",
            )

        return HttpResponseRedirect(reverse("record_list"))


class BorrowRecordReturnRequest(LoginRequiredMixin, View):
    """读者申请还书，管理员收到通知后确认。"""
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        record = get_object_or_404(BorrowRecord, pk=self.kwargs['pk'])

        # 只能操作自己的、状态为 Open 的记录
        if record.user != request.user:
            raise PermissionDenied("你只能归还自己的借阅记录")
        if record.open_or_close != 0:
            messages.warning(request, "该记录不在可归还状态")
            return HttpResponseRedirect(reverse("record_list"))

        record.open_or_close = 2  # Pending Return
        record.save()

        # 通知管理员
        send_notification(
            request.user,
            record,
            verb=f"申请归还《{record.book_title}》",
        )

        UserActivity.objects.create(
            created_by=request.user.username,
            operation_type="warning",
            target_model="BorrowRecord",
            detail=f"'{record.borrower}' 申请归还《{record.book_title}》",
        )

        messages.success(request, "还书申请已提交，请等待管理员确认")
        return HttpResponseRedirect(reverse("record_list"))


class BorrowRecordRejectReturn(AdminRequiredMixin, View):
    """管理员拒绝还书申请，状态恢复为 Open 并通知读者。"""
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        record = get_object_or_404(BorrowRecord, pk=self.kwargs['pk'])
        if record.open_or_close != 2:
            return HttpResponseRedirect(reverse("record_list"))

        record.open_or_close = 0  # 恢复为 Open
        record.save()

        UserActivity.objects.create(
            created_by=request.user.username,
            operation_type="danger",
            target_model="BorrowRecord",
            detail=f"拒绝还书 '{record.borrower}'=>《{record.book_title}》",
        )

        # 通知借阅者：还书被拒绝
        if record.user:
            send_notification_to_user(
                request.user, record.user, record,
                verb=f"拒绝了您归还《{record.book_title}》的申请，请联系管理员",
            )

        messages.info(request, f"已拒绝 {record.borrower} 归还《{record.book_title}》的申请")
        return HttpResponseRedirect(reverse("record_list"))


class BorrowRecordApproveBorrow(AdminRequiredMixin, View):
    """管理员审批通过借阅申请，扣库存，状态改为 Open。"""
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        record = get_object_or_404(BorrowRecord, pk=self.kwargs['pk'])
        if record.open_or_close != 3:
            return HttpResponseRedirect(reverse("record_list"))

        record.open_or_close = 0  # Open
        record.save()

        # 扣库存
        book = record.book_link
        if book:
            book.status = 0
            book.total_borrow_times += 1
            book.quantity -= record.quantity
            book.save()

        UserActivity.objects.create(
            created_by=request.user.username,
            operation_type="success",
            target_model="BorrowRecord",
            detail=f"审批通过 '{record.borrower}' 借阅《{record.book_title}》",
        )

        if record.user:
            send_notification_to_user(
                request.user, record.user, record,
                verb=f"已批准您借阅《{record.book_title}》",
            )

        messages.success(request, f"已批准 {record.borrower} 借阅《{record.book_title}》")
        return HttpResponseRedirect(reverse("record_list"))


class BorrowRecordRejectBorrow(AdminRequiredMixin, View):
    """管理员拒绝借阅申请，删除记录并通知读者。"""
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        record = get_object_or_404(BorrowRecord, pk=self.kwargs['pk'])
        if record.open_or_close != 3:
            return HttpResponseRedirect(reverse("record_list"))

        borrower = record.borrower
        book_title = record.book_title
        borrower_user = record.user

        record.open_or_close = 1  # Closed
        record.final_status = "Rejected"
        record.closed_by = request.user.username
        record.save()

        UserActivity.objects.create(
            created_by=request.user.username,
            operation_type="danger",
            target_model="BorrowRecord",
            detail=f"拒绝 '{borrower}' 借阅《{book_title}》",
        )

        if borrower_user:
            send_notification_to_user(
                request.user, borrower_user, record,
                verb=f"拒绝了您借阅《{book_title}》的申请",
            )

        messages.info(request, f"已拒绝 {borrower} 借阅《{book_title}》的申请")
        return HttpResponseRedirect(reverse("record_list"))


# Data center
@method_decorator(allowed_groups(group_name=['download_data']), name='dispatch')
class DataCenterView(LoginRequiredMixin,TemplateView):
    template_name = 'book/download_data.html'
    login_url = 'login'

    def get(self,request,*args, **kwargs):
        try:
            import pandas as pd
        except ImportError:
            return HttpResponse(
                "[依赖缺失] 数据导出功能需要 pandas，请运行: pip install pandas",
                status=500,
            )
        # check_user_group(request.user,"download_data")
        data = {m.objects.model._meta.db_table:
        {"source":pd.DataFrame(list(m.objects.all().values())) ,
          "path":f"{str(settings.BASE_DIR)}/datacenter/{m.__name__}_{TODAY}.csv",
           "file_name":f"{m.__name__}_{TODAY}.csv"} for m in apps.get_models() if m.__name__ in allowed_models}
        
        count_total = {k: v['source'].shape[0] for k,v in data.items()}
        return render(request,self.template_name,context={'model_list':count_total})

@login_required(login_url='login')
@allowed_groups(group_name=['download_data'])
def download_data(request,model_name):
    try:
        import pandas as pd
    except ImportError:
        return HttpResponse(
            "[依赖缺失] 数据导出功能需要 pandas，请运行: pip install pandas",
            status=500,
        )
    check_user_group(request.user,"download_data")

    download = {m.objects.model._meta.db_table:
        {"source":pd.DataFrame(list(m.objects.all().values())) ,
          "path":f"{str(settings.BASE_DIR)}/datacenter/{m.__name__}_{TODAY}.csv",
           "file_name":f"{m.__name__}_{TODAY}.csv"} for m in apps.get_models() if m.__name__ in allowed_models}

    download[model_name]['source'].to_csv(download[model_name]['path'],index=False,encoding='utf-8')
    download_file=pd.read_csv(download[model_name]['path'],encoding='utf-8')
    response = HttpResponse(download_file,content_type="text/csv")
    response = HttpResponse(open(download[model_name]['path'],'r',encoding='utf-8'),content_type="text/csv")
    response['Content-Disposition'] = f"attachment;filename={download[model_name]['file_name']}"
    return response




# Rankings
class RankingView(LoginRequiredMixin, TemplateView):
    template_name = "book/rankings.html"
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        top_books = Book.objects.order_by('-total_borrow_times')[:10].values_list('title', 'total_borrow_times')
        top_book_titles = [b[0] for b in top_books]
        top_book_counts = [b[1] for b in top_books]

        top_readers = (BorrowRecord.objects
                       .values('borrower')
                       .annotate(count=Count('id'))
                       .order_by('-count')[:10])
        top_reader_names = [r['borrower'] for r in top_readers]
        top_reader_counts = [r['count'] for r in top_readers]

        top_categories = (BorrowRecord.objects
                          .filter(book_link__category__isnull=False)
                          .values('book_link__category__name')
                          .annotate(count=Count('id'))
                          .order_by('-count')[:10])
        top_category_names = [c['book_link__category__name'] for c in top_categories]
        top_category_counts = [c['count'] for c in top_categories]

        # json.dumps ensures safe embedding in JavaScript (no XSS via |safe)
        context['top_book_titles'] = json.dumps(top_book_titles, ensure_ascii=False)
        context['top_book_counts'] = json.dumps(top_book_counts)
        context['top_reader_names'] = json.dumps(top_reader_names, ensure_ascii=False)
        context['top_reader_counts'] = json.dumps(top_reader_counts)
        context['top_category_names'] = json.dumps(top_category_names, ensure_ascii=False)
        context['top_category_counts'] = json.dumps(top_category_counts)
        return context


# AI Smart Search
try:
    from zhipuai import ZhipuAI
except ImportError:
    ZhipuAI = None


def _strip_code_fences(text):
    """Strip markdown code fences (```json ... ```) from LLM output."""
    return re.sub(r'^```\w*\s*|\s*```$', '', text.strip()).strip()


@login_required(login_url='login')
def ai_search(request):
    context = {'results': [], 'query': '', 'error': ''}

    if request.method == 'POST':
        query = request.POST.get('ai_query', '').strip()
        context['query'] = query

        if not query:
            return render(request, 'book/ai_search.html', context)

        if ZhipuAI is None:
            context['error'] = '未安装 zhipuai 依赖，请运行: uv sync'
            return render(request, 'book/ai_search.html', context)

        api_key = settings.ZHIPUAI_API_KEY
        if not api_key:
            context['error'] = '未配置智谱AI API Key，请在 .env 文件中设置 ZHIPUAI_API_KEY。'
            return render(request, 'book/ai_search.html', context)

        # Limit catalog to 500 books to stay within LLM context window
        book_rows = (Book.objects
                     .select_related('category')
                     .order_by('-total_borrow_times')
                     .values_list('title', 'author', 'category__name', 'description')[:500])
        if not book_rows:
            context['error'] = '图书库中暂无图书数据。'
            return render(request, 'book/ai_search.html', context)

        catalog_lines = []
        for title, author, cat_name, desc in book_rows:
            catalog_lines.append(
                f"《{title}》 作者:{author} 分类:{cat_name or '未分类'} 简介:{(desc or '')[:100]}"
            )
        catalog = '\n'.join(catalog_lines)

        try:
            client = ZhipuAI(api_key=api_key)
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "system", "content": (
                        "你是一个图书馆智能助手。用户会描述他们想找的书或感兴趣的内容。\n"
                        "请根据以下图书目录，推荐最匹配的图书（最多5本）。\n"
                        "对每本推荐的书，返回JSON数组格式：[{\"title\": \"书名\", \"reason\": \"推荐理由\"}]\n"
                        "只返回JSON数组，不要包含其他内容。如果没有匹配的书，返回空数组 []。\n\n"
                        f"图书目录：\n{catalog}"
                    )},
                    {"role": "user", "content": query},
                ],
            )

            ai_text = _strip_code_fences(response.choices[0].message.content)
            recommendations = json.loads(ai_text)

            # Batch-match all recommended titles in a single query
            title_q = Q()
            for rec in recommendations:
                t = rec.get('title', '').strip().strip('《》')
                rec['title'] = t
                if t:
                    title_q |= Q(title__icontains=t)

            matched_books = {}
            if title_q:
                for book in Book.objects.select_related('category').filter(title_q):
                    matched_books.setdefault(book.title.lower(), book)

            results = []
            for rec in recommendations:
                title = rec.get('title', '')
                reason = rec.get('reason', '')
                book = matched_books.get(title.lower()) or matched_books.get(title)
                if not book:
                    for key, val in matched_books.items():
                        if title.lower() in key or key in title.lower():
                            book = val
                            break
                results.append({'title': title, 'reason': reason, 'book': book})
            context['results'] = results

        except json.JSONDecodeError:
            context['error'] = 'AI 返回的数据格式异常，请重试。'
        except Exception as e:
            logger.error(f"AI search error: {e}")
            context['error'] = 'AI 服务暂时不可用，请稍后重试。'

    return render(request, 'book/ai_search.html', context)


# Handle Errors

def page_not_found(request, exception):
    context = {}
    response = render(request, "errors/404.html", context=context)
    response.status_code = 404
    return response
    
def server_error(request, exception=None):
    context = {}
    response = render(request, "errors/500.html", context=context)
    response.status_code = 500
    return response
    
def permission_denied(request, exception=None):
    context = {}
    response = render(request, "errors/403.html", context=context)
    response.status_code = 403
    return response
    
def bad_request(request, exception=None):
    context = {}
    response = render(request, "errors/400.html", context=context)
    response.status_code = 400
    return response

# Employees
# @method_decorator(user_passes_test(lambda u: check_superuser(u)), name='dispatch')
class EmployeeView(SuperUserRequiredMixin,ListView):
    login_url = 'login'
    model=User
    context_object_name = 'employees'
    template_name = 'book/employees.html'

    def get_queryset(self):
        return User.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True)
        ).distinct().order_by('username')

    # def get(self, request):
    #     # check_superuser(request.user)
    #     return super(EmployeeView, self).get(self,request)

# @method_decorator(user_passes_test(lambda u: check_superuser(u)), name='dispatch')
class EmployeeDetailView(SuperUserRequiredMixin,DetailView):
    model = User
    context_object_name = 'employee'
    template_name = 'book/employee_detail.html'
    login_url = 'login'

    def get_queryset(self):
        return User.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = user_groups
        return context


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url='login')
def EmployeeUpdate(request, pk):
    current_user = get_object_or_404(
        User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).distinct(),
        pk=pk,
    )
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=current_user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = form.cleaned_data['is_staff']
            user.is_active = form.cleaned_data['is_active']
            user.is_superuser = form.cleaned_data['is_superuser']
            new_pw = form.cleaned_data.get('new_password')
            if new_pw:
                user.set_password(new_pw)
            user.save()
            user.groups.set(form.cleaned_data['groups'])
            UserActivity.objects.create(
                created_by=request.user.username,
                operation_type="warning",
                target_model='User',
                detail=f"Update Employee << {user.username} >>",
            )
            messages.success(request, f"员工 << {user.username} >> 信息已更新")
            return redirect('employees_detail', pk=pk)
    else:
        form = EmployeeEditForm(instance=current_user, initial={
            'groups': current_user.groups.all(),
            'is_staff': current_user.is_staff,
            'is_active': current_user.is_active,
            'is_superuser': current_user.is_superuser,
        })
    return render(request, 'book/employee_detail.html', {'form': form, 'employee': current_user})


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url='login')
def EmployeeCreate(request):
    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = form.cleaned_data['is_staff']
            user.is_superuser = form.cleaned_data['is_superuser']
            user.save()
            user.groups.set(form.cleaned_data['groups'])
            UserActivity.objects.create(
                created_by=request.user.username,
                target_model='User',
                detail=f"Create Employee << {user.username} >>",
            )
            messages.success(request, f"员工 << {user.username} >> 已创建")
            return redirect('employees_list')
    else:
        form = EmployeeCreateForm()
    return render(request, 'book/employee_create.html', {'form': form})


# Notice

class NoticeListView(LoginRequiredMixin, ListView):
    context_object_name = 'notices'
    template_name = 'notice_list.html'
    login_url = 'login'

    # 未读通知的查询集
    def get_queryset(self):
        return self.request.user.notifications.unread()


class NoticeUpdateView(LoginRequiredMixin,View):
    """Update Status of Notification"""
    # 处理 get 请求
    def get(self, request):
        # 获取未读消息
        notice_id = request.GET.get('notice_id')
        # 更新单条通知
        if notice_id:
            request.user.notifications.get(id=notice_id).mark_as_read()
            return redirect('category_list')
        # 更新全部通知
        else:
            request.user.notifications.mark_all_as_read()
            return redirect('notice_list')
