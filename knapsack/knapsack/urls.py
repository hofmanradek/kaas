"""knapsack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

import kaas.views as views
import kaas.api.endpoints as endpoints

API_PREFIX = 'api/v1/'

urlpatterns = [
    #django admin
    url(r'^admin/', admin.site.urls),

    #REST API
    url(r'^{}tasks/$'.format(API_PREFIX), endpoints.KnapsackTaskListAPI.as_view(), name='api_task_list'),
    url(r'^{}tasks/(?P<task_id>[-a-z0-9]+)/$'.format(API_PREFIX), endpoints.KnapsackTaskDetailAPI.as_view(), name='api_task_detail'),

    #web views handlers
    url(r'^$', views.index),  # index page
    url(r'^solve/', views.solve, name='solve'),  # task submission page
    url(r'^dashboard/', views.dashboard, name='dashboard'),  # task dashboard

    # login / logout urls
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^logout-then-login/$', auth_views.logout_then_login, name='logout_then_login'),

    #register new user
    url(r'^register/$', views.register, name='register'),

    # change password urls
    url(r'^password-change/$', auth_views.password_change, name='password_change'),
    url(r'^password-change/done/$', auth_views.password_change_done, name='password_change_done'),

    # restore password urls - email backend required...but forms we have:)
    url(r'^password-reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password-reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password-reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
]
