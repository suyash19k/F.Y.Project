# dreams/urls.py
from django.urls import path
from . import views

# The app_name is essential for namespacing
app_name = 'dreams'

urlpatterns = [
    path('', views.dashboard_view, name='dreams_index'),  # Add this line
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add/', views.add_dream_view, name='add_dream'),
    path('results/<int:dream_id>/', views.dream_results_view, name='dream_results'),
]