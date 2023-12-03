"""py_karaoke URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from videos.views import video_details, queue, search, add, remove

urlpatterns = [
    path('admin/', admin.site.urls)
    ,path(r'^$', queue, name='queue')
    ,path('queue/', queue, name='queue')
    ,path('search/', search, name='search')
    ,path('add/', add, name='add')
    ,path('remove/', remove, name='remove')
    ,path('video/<str:video_id>', video_details, name='video_details')

]
