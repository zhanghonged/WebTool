# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import logout
from django.shortcuts import render_to_response
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
import time

'''以下这些函数是渲染前端模板的函数'''
# 服务器的名字
htmltitle = '服务器工具'


@login_required(login_url='/loginpage')
def homepage(request):
    username = request.session.get('username')
    pagedict = {'title': htmltitle, 'username': username}
    return render_to_response('servermaterial/home.html', pagedict)


@login_required(login_url='/loginpage')
def realtimelog(request):
    username = request.session.get('username')
    pagedict = {'title': htmltitle, 'username': username}
    return render_to_response("servermaterial/realtimelog.html", pagedict)

@login_required(login_url='/loginpage')
def mylog(request):
    username = request.session.get('username')
    pagedict = {'title': htmltitle, 'username': username}
    return render_to_response("servermaterial/mylog.html", pagedict)

@login_required(login_url='/loginpage')
def log(request):
    username = request.session.get('username')
    pagedict = {'title': htmltitle, 'username': username}
    return render_to_response("servermaterial/log.html", pagedict)


@login_required(login_url='/loginpage')
def servertime(request):
    from WebTool.functions import get_server_time
    from server import models
    taskor = ''
    try:
        taskor = models.taskinbackground.objects.get(taskname='usingtime').taskor
    except Exception as e:
        print e
    username = request.session.get('username')
    # 取出数据库后10条修改时间的数据
    modifytimes = models.modifytime.objects.all()[::-1][0:10]
    pagedict = {'time': get_server_time(), 'modifytimes': modifytimes, 'title': htmltitle, 'username': username}
    # 本人在使用服务器
    if taskor == username:
        pagedict['serverstatus'] = 'self'
    # 无人使用服务器
    elif taskor == '':
        pagedict['serverstatus'] = 'nobady'
    # 其他人在使用服务器
    else:
        pagedict['serverstatus'] = 'others'
        pagedict['taskor'] = taskor
    return render_to_response('servermaterial/servertime.html', pagedict)


@login_required(login_url='/loginpage')
def rebootserver(request):
    from server import models
    username = request.session.get('username')
    # 取出数据库后10条重启的数据
    reboot = models.rebootserver.objects.all()[::-1][0:10]
    taskor = ''
    try:
        taskor = models.taskinbackground.objects.get(taskname='reboot').taskor
    except Exception as e:
        print e
    pagedict = {'reboot': reboot, 'title': htmltitle, 'taskor': taskor, 'username': username}
    return render_to_response("servermaterial/reboot.html", pagedict)


@login_required(login_url='/loginpage')
def serverconfig(request):
    from server import models
    username = request.session.get('username')
    name_list = []
    config_name = models.serverconfig.objects.all().values_list('id', 'config_name', 'detail')
    for name in config_name:
        name_list.append(name)
    pagedict = {'name_list': name_list, 'title': htmltitle, 'username': username}
    return render_to_response("servermaterial/serverconfig.html", pagedict)


@login_required(login_url='/loginpage')
def help(request):
    username = request.session.get('username')
    pagedict = {'title': htmltitle, 'username': username}
    return render_to_response('servermaterial/help.html', pagedict)


@login_required(login_url='/loginpage')
def user_config(request):
    username = request.session.get('username')
    pagedict = {'title': htmltitle, 'username': username}
    return render_to_response('servermaterial/authority.html', pagedict)


'''以下这些函数是处理url转过来网站页面逻辑'''


# get server time by button
def getservertime(request):
    if request.method == 'GET':
        ret = {'status': False, 'time': '', 'error': ''}
        try:
            from WebTool.functions import get_server_time
            ret['time'] = get_server_time()
            ret['status'] = True
        except Exception, e:
            ret['status'] = False
            ret['error'] = str(e)
            return JsonResponse(ret)
        return JsonResponse(ret)


# recover local time
def recoverlocaltime(request):
    if request.method == 'GET':
        ret = {'status': False}
        try:
            from WebTool.functions import restore_server_time
            from server import models
            restore_server_time()
            local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            username = request.session.get('username')
            models.modifytime.objects.create(modifyer=username, modifytime=local_time, modifyservertime=local_time)
            ret['status'] = True
            ret['modifytime'] = local_time
            ret['modifyer'] = username
        except Exception, e:
            ret['status'] = False
            return JsonResponse(ret)
        return JsonResponse(ret)


# set server time
def settime(request):
    if request.method == 'POST':
        ret = {'status': False}
        try:
            from WebTool.functions import modify_server_time
            from server import models
            servertime = request.POST.get('settime')
            modify_server_time(servertime)
            local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print 'as'
            username = request.session.get('username')
            models.modifytime.objects.create(modifyer=username, modifytime=local_time, modifyservertime=servertime)
            ret['modifytime'] = local_time
            ret['servertime'] = servertime
            ret['modifyer'] = username
            ret['status'] = True
        except Exception, e:
            ret['status'] = False
            return JsonResponse(ret)
        return JsonResponse(ret)


# reboot server
def restartserver(request):
    if request.method == 'GET':
        ret = {'status': False}
        from WebTool.functions import rebootserver
        from server import models
        username = request.session.get('username')
        models.taskinbackground.objects.filter(taskname='reboot').delete()
        models.taskinbackground.objects.create(taskname='reboot', taskor=username)
        res = rebootserver()
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if res == 'Successful Rebooted!':
            ret['status'] = True
            models.rebootserver.objects.create(rebooter=username, reboottime=local_time, rebootresult='重启成功')
            models.taskinbackground.objects.filter(taskname='reboot').delete()
            return JsonResponse(ret)
        elif res == 'Unsuccessful Rebooted!':
            models.rebootserver.objects.create(rebooter=username, reboottime=local_time, rebootresult='重启失败')
            models.taskinbackground.objects.filter(taskname='reboot').delete()
            ret['status'] = False
            return JsonResponse(ret)
        else:
            models.rebootserver.objects.create(rebooter=username, reboottime=local_time, rebootresult='重启失败')
            models.taskinbackground.objects.filter(taskname='reboot').delete()
            ret['status'] = False
            return JsonResponse(ret)


# 获得服务器配置
def getconfig(request):
    from server import models
    if request.method == 'GET':
        ret = {'status': False}
        from WebTool.functions import get_serverconfig_lists, read_serverconfig
        newconfigs = get_serverconfig_lists()
        name_list = models.serverconfig.objects.all().values('config_name')
        oldconfigs = []
        for name in name_list:
            oldconfigs.append(str(name['config_name']))
        # common configs
        common = [name for name in newconfigs if name in oldconfigs]
        for config in common:
            configcontent = read_serverconfig(config)
            models.serverconfig.objects.filter(config_name=config).update(content=configcontent)
        # add configs
        add_con = [name for name in newconfigs if name not in oldconfigs]
        for config in add_con:
            configcontent = read_serverconfig(config)
            models.serverconfig.objects.create(config_name=config, content=configcontent)
        # delete configs
        delete_con = [name for name in oldconfigs if name not in newconfigs]
        for config in delete_con:
            models.serverconfig.objects.filter(config_name=config).delete()
        ret['status'] = True
        return JsonResponse(ret)


# get config content
def readconfig(request):
    ret = {'status': False, 'content': ''}
    if request.method == 'POST':
        from server import models
        name = request.POST.get('configname')
        content = models.serverconfig.objects.get(config_name=name).content
        ret['status'] = True
        ret['content'] = content
        return JsonResponse(ret)
    return JsonResponse(ret)


# write config
def writeconfig(request):
    ret = {'status': False, 'error': '', 'oldcontent': ''}
    if request.method == 'POST':
        from server import models
        from WebTool.functions import generate_config_upload_file
        name = request.POST.get('name')
        newcontent = request.POST.get('content')
        try:
            json.loads(newcontent)
        except ValueError:
            oldcontent = models.serverconfig.objects.get(config_name=name).content
            ret['oldcontent'] = oldcontent
            ret['error'] = '1'
            return JsonResponse(ret)
        rtn = generate_config_upload_file(name, newcontent)
        if rtn == 'Successful Upload':
            models.serverconfig.objects.filter(config_name=name).update(content=newcontent)
            ret['status'] = True
            return JsonResponse(ret)
        else:
            oldcontent = models.serverconfig.objects.get(config_name=name).content
            ret['oldcontent'] = oldcontent
            ret['error'] = '2'
            return JsonResponse(ret)


# delete config
def deleteconfig(request):
    ret = {'status': False}
    if request.method == 'POST':
        from server import models
        from WebTool.functions import delete_config
        name = request.POST.get('name')
        try:
            models.serverconfig.objects.filter(config_name=name).delete()
            delete_config(name)
            ret['status'] = True
            return JsonResponse(ret)
        except Exception:
            ret['status'] = False
        return JsonResponse(ret)


# add detail of config
def configdetail(request):
    ret = {'status': False}
    if request.method == 'POST':
        detail = request.POST.get('detail')
        name = request.POST.get('name')
        from server import models
        models.serverconfig.objects.filter(config_name=name).update(detail=detail)
        ret['status'] = True
        return JsonResponse(ret)


# search plog
def searchlog(request):
    ret = {'status': False, 'logs': ''}
    if request.method == 'POST':
        from WebTool.functions import get_filter_log
        keycontent = request.POST.get('keycontent')
        logdate = request.POST.get('date')
        logtime = request.POST.get('time')
        filter_list = [keycontent, logdate, logtime]
        logs = get_filter_log(filter_list)
        ret['status'] = True
        ret['logs'] = logs
    return JsonResponse(ret)


# 有人使用服务器，别人无法修改时间
def usingserver(request):
    ret = {'status': False}
    if request.method == 'GET':
        status = request.GET.get('using')
        from server import models
        if status == 'yes':
            username = request.session.get('username')
            models.taskinbackground.objects.filter(taskname='usingtime').delete()
            models.taskinbackground.objects.create(taskname='usingtime', taskor=username)
            ret['status'] = True
            return JsonResponse(ret)
        if status == 'no':
            models.taskinbackground.objects.filter(taskname='usingtime').delete()
            ret['status'] = True
            return JsonResponse(ret)


# 用户登出
def userlogout(request):
    ret = {'status': True}
    if request.method == 'GET':
        # 登出
        logout(request)
        return JsonResponse(ret)
