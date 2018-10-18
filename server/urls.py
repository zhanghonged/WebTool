from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.homepage),
    url(r'^home', views.homepage),

    url(r'^servertime', views.servertime),
    url(r'^realtimelog', views.realtimelog),
    url(r'^mylog', views.mylog),
    url(r'^log', views.log),
    url(r'^reboot', views.rebootserver),
    url(r'^serverconfig', views.serverconfig),
    url(r'^authority', views.user_config),
    url(r'^help', views.help),

    url(r'^settime', views.settime),
    url(r'^getconfig', views.getconfig),
    url(r'^readconfig', views.readconfig),
    url(r'^searchlog', views.searchlog),
    url(r'^writeconfig', views.writeconfig),
    url(r'^usingserver', views.usingserver),
    url(r'^deleteconfig', views.deleteconfig),
    url(r'^configdetail', views.configdetail),
    url(r'^restartserver', views.restartserver),
    url(r'^getservertime', views.getservertime),
    url(r'^recoverlocaltime', views.recoverlocaltime),
    url(r'^userlogout', views.userlogout),
]
