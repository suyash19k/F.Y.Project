# dreams/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from .models import DreamNarration
import plotly.express as px
import pandas as pd
from collections import Counter

@admin.register(DreamNarration)
class DreamNarrationAdmin(admin.ModelAdmin):
    """
    This class configures the admin pages and includes the
    integrated dashboard with robust, crash-proof charting.
    """
    list_display = ('user', 'sentiment', 'emotion', 'risk_level', 'created_at')
    list_filter = ('risk_level', 'sentiment', 'emotion')
    search_fields = ('dream_text', 'user__username')
    readonly_fields = ('analysis_json', 'created_at')

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path(
                "dashboard/",
                self.admin_site.admin_view(self.dashboard_view),
                name='%s_%s_dashboard' % info
            ),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """
        This view renders the dashboard and is robust against bad data.
        """
        total_dreams = DreamNarration.objects.count()
        risk_stats = DreamNarration.objects.values("risk_level").annotate(count=Count("id")).order_by('-count')
        sentiment_stats = DreamNarration.objects.values("sentiment").annotate(count=Count("id")).order_by('-count')
        
        all_emotions_raw = DreamNarration.objects.values_list('emotion', flat=True)
        clean_emotions = [str(e) for e in all_emotions_raw if isinstance(e, str)]
        emotion_counts = Counter(clean_emotions)
        emotion_stats = [{'emotion': emo, 'count': count} for emo, count in emotion_counts.items()]

        # Chart Generation
        risk_df = pd.DataFrame(list(risk_stats))
        risk_chart = None
        if not risk_df.empty and 'risk_level' in risk_df.columns:
            fig = px.pie(risk_df, names='risk_level', values='count', title='Risk Level Distribution')
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            risk_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')

        sentiment_df = pd.DataFrame(list(sentiment_stats))
        sentiment_chart = None
        if not sentiment_df.empty and 'sentiment' in sentiment_df.columns:
            fig = px.bar(sentiment_df, x='sentiment', y='count', title='Sentiment Distribution', color='sentiment')
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            sentiment_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')
            
        emotion_df = pd.DataFrame(emotion_stats)
        emotion_chart = None
        if not emotion_df.empty and 'emotion' in emotion_df.columns:
            fig = px.bar(emotion_df, x='emotion', y='count', title='Top Emotions', color='emotion')
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
            emotion_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')

        context = {
            "title": "Dream Analysis Dashboard",
            "total_dreams": total_dreams,
            "risk_chart": risk_chart,
            "sentiment_chart": sentiment_chart,
            "emotion_chart": emotion_chart,
        }
        
        return render(request, "admin/dreams/dashboard.html", context)

    def changelist_view(self, request, extra_context=None):
        """Adds a 'View Dashboard' button to the main list page."""
        extra_context = extra_context or {}
        dashboard_url = reverse('admin:dreams_dreamnarration_dashboard')
        
        extra_context['dashboard_button'] = format_html(
            '<a href="{}" class="button">View Dashboard</a>', dashboard_url
        )
        return super().changelist_view(request, extra_context=extra_context)

    # --- THIS FUNCTION HAS BEEN REMOVED ---
    # def add_view(self, request, form_url="", extra_context=None):
    #     """Redirects the 'Add' button to the dashboard."""
    #     return redirect(reverse("admin:dreams_dreamnarration_dashboard"))