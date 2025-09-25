# dream_analyzer/urls.py

from django.contrib import admin
from django.urls import path, include
from .views import home_view

urlpatterns = [
    path('', home_view, name='home'),  # Homepage
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dreams/', include(('dreams.urls', 'dreams'), namespace='dreams')),
]