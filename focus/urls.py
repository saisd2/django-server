"""focus URL Configuration

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
from django.urls import path, re_path
from focus_user import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("create_user/", views.create_user),
    path("login/", views.login_user),
    path("logout/", views.logout_user),
    path("upload/", views.upload_image),
    path("users/", views.get_users),
    path("follow/", views.follow_user),
    path("unfollow/", views.unfollow_user),
    path("uploads/<str:category>/", views.get_filtered_uploads),
    path("uploads/", views.get_uploads),
    path("upload/<str:upload_id>", views.handle_upload_by_id),
    path("user/<str:user>/", views.get_user),
    path("user/", views.get_logged_in_user),
    path("comment/", views.create_comment),
    path("rate/", views.add_rating)
]
