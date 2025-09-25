# dream_analyzer/views.py

from django.shortcuts import render
from dreams.models import DreamNarration
from dreams.forms import DreamForm

def home_view(request):
    context = {}
    if request.user.is_authenticated:
        user_dreams = DreamNarration.objects.filter(user=request.user).order_by('-created_at')[:5]
        context['dreams'] = user_dreams
        context['form'] = DreamForm()
    return render(request, 'main/home.html', context)