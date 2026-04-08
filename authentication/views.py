# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .forms import LoginForm, SignUpForm


ROLE_LOGIN_CONFIG = [
    {
        "key": "superadmin",
        "label": "超级管理员",
        "username": "demo_admin",
        "password": "Demo@123456",
        "description": "拥有后台、员工、通知和全站管理权限。",
        "icon": "feather icon-shield",
        "is_superuser": True,
        "is_staff": True,
        "groups": ["download_data", "logs", "api"],
    },
    {
        "key": "librarian",
        "label": "图书管理员",
        "username": "demo_librarian",
        "password": "Demo@123456",
        "description": "可管理图书、会员、借阅记录和数据下载。",
        "icon": "feather icon-book",
        "is_superuser": False,
        "is_staff": True,
        "groups": ["download_data", "logs", "api"],
    },
    {
        "key": "reader",
        "label": "普通读者",
        "username": "demo_reader",
        "password": "Demo@123456",
        "description": "查看首页与个人借阅记录，模拟普通用户视角。",
        "icon": "feather icon-user",
        "is_superuser": False,
        "is_staff": False,
        "groups": [],
    },
]


def get_role_login_options():
    if not settings.ROLE_LOGIN_ENABLED:
        return []
    return ROLE_LOGIN_CONFIG


def ensure_role_login_user(role_key):
    role = next((item for item in ROLE_LOGIN_CONFIG if item["key"] == role_key), None)
    if role is None:
        return None

    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username=role["username"],
        defaults={
            "email": f'{role["username"]}@demo.local',
            "is_active": True,
        },
    )
    user.is_superuser = role["is_superuser"]
    user.is_staff = role["is_staff"]
    user.is_active = True
    user.email = user.email or f'{role["username"]}@demo.local'
    user.first_name = role["label"]
    user.set_password(role["password"])
    user.save()

    if role["groups"]:
        groups = [Group.objects.get_or_create(name=name)[0] for name in role["groups"]]
        user.groups.set(groups)
    else:
        user.groups.clear()

    from book.models import Profile
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = None

    if profile is None:
        Profile.objects.create(
            user=user,
            bio=f'{role["label"]}演示账号',
            email=user.email,
        )
    else:
        profile.email = user.email
        if not profile.bio:
            profile.bio = f'{role["label"]}演示账号'
        profile.save(update_fields=["email", "bio"])

    return user


def role_login_view(request, role_key):
    if not settings.ROLE_LOGIN_ENABLED:
        return redirect("login")

    user = ensure_role_login_user(role_key)
    if user is None:
        return redirect("login")

    login(request, user)
    return redirect("/")


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":
        role_key = request.POST.get("role_login")
        if role_key:
            if not settings.ROLE_LOGIN_ENABLED:
                msg = '当前环境未开启角色一键登录'
            else:
                user = ensure_role_login_user(role_key)
                if user is not None:
                    login(request, user)
                    return redirect("/")
                msg = '未找到对应角色账号'
        else:
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect("/")
                else:
                    msg = '用户名或密码无效'
            else:
                msg = '验证表单时出错'

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "msg": msg,
            "role_logins": get_role_login_options(),
            "role_login_enabled": settings.ROLE_LOGIN_ENABLED,
        },
    )

def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg     = '用户已创建 - 请<a href="/login">登录</a>.'
            success = True
            
            #return redirect("/login/")

        else:
            msg = '表单无效'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })
