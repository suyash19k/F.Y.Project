# dreams/models.py
from django.db import models
from .ai_pipeline import analyze_dream


class DreamNarration(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="dreams")
    dream_text = models.TextField()

    # Auto-filled fields
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    emotion = models.JSONField(blank=True, null=True)
    potential_condition = models.CharField(max_length=100, blank=True, null=True)
    risk_level = models.CharField(max_length=20, blank=True, null=True)
    analysis_json = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.dream_text:
            try:
                result = analyze_dream(self.dream_text)
                self.sentiment = result["sentiment_label"]
                self.emotion = result["emotion_summary"]
                self.potential_condition = result["potential_condition"]
                self.risk_level = result["risk_level"]
                self.analysis_json = result["analysis_json"]
            except Exception as e:
                # Fallback so migrations/admin don't break
                self.sentiment = "Error"
                self.emotion = {"error": str(e)}
                self.potential_condition = "Unknown"
                self.risk_level = "Low"
                self.analysis_json = {}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dream by {self.user} on {self.created_at:%Y-%m-%d}"
