from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class DreamNarration(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="account_dreams")
    dream_text = models.TextField()
    sentiment = models.CharField(max_length=32, blank=True, null=True)
    emotion = models.CharField(max_length=128, blank=True, null=True)
    analysis_json = models.JSONField(blank=True, null=True)
    potential_condition = models.CharField(max_length=128, blank=True, null=True)
    risk_level = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"