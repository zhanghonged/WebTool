# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate


# 登陆页面
def loginpage(request):
    return render_to_response("loginpage.html")


# 创建账户
def createuser(request):
    ret = {'status': False, 'reason': ''}
    if request.method == 'POST':
        username = request.POST.get('user')
        email = request.POST.get('email')
        password = request.POST.get('code')
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except Exception as e:
            if e[0] == 1062:
                ret['reason'] = 'repeated'
                ret['status'] = False
                return JsonResponse(ret)
        ret['status'] = True
        return JsonResponse(ret)


# 用户登陆
def userlogin(request):
    ret = {'status': False, 'reason': ''}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            # 将用户名记录在session中
            request.session['username'] = username
            if user.is_active:
                login(request, user)
                ret['status'] = True
        else:
            ret['reason'] = 'codewrong'
        return JsonResponse(ret)


# 忘记密码
def forgetusr(request):
    ret = {'status': False, 'reason': ''}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        newpassword = request.POST.get('newpassword')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 账号不存在
            ret['reason'] = 'unexist'
            return JsonResponse(ret)
        email_ = User.objects.get(username=user).email
        # 用户名对应邮箱错误
        if email_ != email:
            ret['reason'] = 'emailwrong'
            return JsonResponse(ret)
        user.set_password(newpassword)
        user.save()
        ret['status'] = True
        return JsonResponse(ret)






