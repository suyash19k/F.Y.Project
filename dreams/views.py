# dreams/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DreamForm, DreamAudioForm
from .models import DreamNarration
from .ai_pipeline import analyze_dream
import json

@login_required
def home(request):
    return render(request, 'dreams/home.html')

@login_required
def dashboard_view(request):
    """
    Displays a dashboard with correctly calculated statistics about the user's dreams.
    """
    user_dreams = DreamNarration.objects.filter(user=request.user)

    # Total dreams
    total_dreams_count = user_dreams.count()

    # Lucid dreams (define as emotion == 'Joy')
    lucid_dreams_count = user_dreams.filter(emotion__iexact='Joy').count()

    # Nightmares (define as risk_level == 'High')
    nightmare_count = user_dreams.filter(risk_level__iexact='High').count()

    context = {
        'total_dreams': total_dreams_count,
        'lucid_dreams': lucid_dreams_count,
        'nightmare_count': nightmare_count,
        'dreams': user_dreams.order_by('-created_at')[:10],  # Show 10 most recent dreams
    }
    return render(request, 'dreams/dashboard.html', context)

@login_required
def add_dream_view(request):
    """
    Handles the form for adding a new dream and processing it.
    """
    if request.method == 'POST':
        form = DreamForm(request.POST)
        if form.is_valid():
            dream = form.save(commit=False)
            dream.user = request.user

            analysis_output = analyze_dream(dream.dream_text)

            # Get the dictionary of emotion scores and find the primary emotion
            emotion_summary = analysis_output.get("emotion_summary", {})
            primary_emotion = "N/A"
            if isinstance(emotion_summary, dict) and emotion_summary:
                primary_emotion = max(emotion_summary, key=emotion_summary.get)

            dream.sentiment = analysis_output.get("sentiment_label", "N/A")
            dream.emotion = primary_emotion.capitalize()
            dream.potential_condition = analysis_output.get("potential_condition", "N/A")
            dream.risk_level = analysis_output.get("risk_level", "N/A")
            dream.analysis_json = analysis_output.get("analysis_json", {})

            dream.save()
            return redirect('dreams:dream_results', dream_id=dream.id)
    else:
        form = DreamForm()
    return render(request, 'dreams/add_dream.html', {'form': form})

@login_required
def add_dream_audio_view(request):
    """
    Handles the form for adding a new dream via an audio file.
    """
    if request.method == 'POST':
        form = DreamAudioForm(request.POST, request.FILES)
        if form.is_valid():
            dream_text = f"Audio file uploaded: {request.FILES['audio_file'].name}. Transcription pending."
            dream = DreamNarration.objects.create(user=request.user, dream_text=dream_text, risk_level="Pending")
            return redirect('dreams:dream_results', dream_id=dream.id)
    else:
        form = DreamAudioForm()
    return render(request, 'dreams/add_dream_audio.html', {'form': form})

@login_required
def dream_results_view(request, dream_id):
    """
    Displays the full analysis results for a specific dream.
    """
    dream = get_object_or_404(DreamNarration, id=dream_id, user=request.user)

    pretty_json = ""
    if dream.analysis_json:
        try:
            json_data = dream.analysis_json if isinstance(dream.analysis_json, dict) else json.loads(str(dream.analysis_json))
            pretty_json = json.dumps(json_data, indent=4)
        except (TypeError, json.JSONDecodeError):
            pretty_json = str(dream.analysis_json)

    context = {
        'dream': dream,
        'pretty_json': pretty_json
    }
    return render(request, 'dreams/dream_results.html', context)

