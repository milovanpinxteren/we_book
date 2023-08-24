from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('', include("bookingsystem.urls", namespace='bookingsystem'))
]

urlpatterns += i18n_patterns(
    path('', include("bookingsystem.urls", namespace='bookingsystem'))
)
