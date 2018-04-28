# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from . import views
from mmb import views as mmb_views

urlpatterns = [
    # Examples:
    # url(r'^$', 'zcspider.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),  # 首页
    url(r'login/', views.login, name='login'),  # 登陆页面
    url(r'register/', views.register, name='register'),  # 注册页面
    url(r'mmb_round/', mmb_views.mmb_round, name='mmb_round'),  # mmb循环跑
    url(r'mmb_model4/', mmb_views.mmb_model4, name='mmb_model4'),  # mmb模式4指定words 主页面
    url(r'mmb_model5/', mmb_views.mmb_model5, name='mmb_model5'),  # mmb模式5指定model 主页面
    url(r'designed_words/', mmb_views.designed_words, name='designed_words'),  # 执行定制words
    url(r'designed_models/', mmb_views.designed_models, name='designed_models'),  # 执行定制models
    url(r'show_pro/', mmb_views.show_pro, name='show_pro'),
    url(r'test', views.test1),

]
