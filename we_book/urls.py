from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.contrib.auth import views as auth_views

from bookingsystem.views.auth_views import CustomLoginView, ChangePasswordView

urlpatterns = [
    path('login', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('show_change_password_page', ChangePasswordView.as_view(), name='show_change_password_page'),


    path('admin/', admin.site.urls),
    path('', include("bookingsystem.urls", namespace='bookingsystem'))
]

urlpatterns += i18n_patterns(
    path('', include("bookingsystem.urls", namespace='bookingsystem')),
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('show_change_password_page', ChangePasswordView.as_view(), name='show_change_password_page'),

)

