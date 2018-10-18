# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class serverconfig(models.Model):
    id = models.AutoField(primary_key=True)
    config_name = models.CharField(max_length=100)
    content = models.TextField()
    detail = models.CharField(max_length=200, default="")

    class Meta:
        db_table = 'serverconfig'
        app_label = "server"


class taskinbackground(models.Model):
    taskname = models.CharField(max_length=50)
    taskor = models.CharField(max_length=100)

    class Meta:
        db_table = 'task'
        app_label = "server"


class modifytime(models.Model):
    modifyer = models.CharField(max_length=100)
    modifytime = models.CharField(max_length=200, default="")
    modifyservertime = models.CharField(max_length=200, default="")

    class Meta:
        db_table = 'modifytime'
        app_label = "server"


class rebootserver(models.Model):
    rebooter = models.CharField(max_length=100)
    reboottime = models.CharField(max_length=200, default="")
    rebootresult = models.CharField(max_length=200, default="")

    class Meta:
        db_table = 'reboot'
        app_label = "server"
