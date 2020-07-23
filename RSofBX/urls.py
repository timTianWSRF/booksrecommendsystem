"""RSofBX URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from RSofBX.apps.bxdb import views as bxviews
from RSofBX.apps.rs_offline import views as offviews
from face.views import index, camera

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', bxviews.login.as_view()),
    path('logout/', bxviews.logout.as_view()),
    path('justlooking/', bxviews.topN.as_view()),
    path('register/', bxviews.register.as_view()),
    path('bookdetail/<int:bid>/', bxviews.bookDetail.as_view()),
    path('background/', offviews.backTraining.as_view()),
    path('home/', bxviews.home.as_view()),
    path('search/tag/<str:tag>/', bxviews.search.as_view()),
    path('search/', bxviews.search.as_view()),
    path('rate/', bxviews.setmyRate),
    path('newUserRating/', bxviews.newUserRating.as_view()),

    url(r'^$', bxviews.logout.as_view()),
    url(r'^index/', index),
    url(r'^camera/', camera),
    path('test/', bxviews.test.as_view()),
]
