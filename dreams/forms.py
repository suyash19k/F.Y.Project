from django import forms
from .models import DreamNarration

class DreamForm(forms.ModelForm):
    class Meta:
        model = DreamNarration
        fields = ["dream_text"]
        widgets = {
            "dream_text": forms.Textarea(attrs={"rows":5, "placeholder":"Describe your dream..."}),
        }
class DreamAudioForm(forms.Form):
    audio_file = forms.FileField(label="Upload Dream Audio file")