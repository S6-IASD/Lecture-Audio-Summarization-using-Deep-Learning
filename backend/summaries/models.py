from django.db import models
from django.conf import settings


class Summary(models.Model):
    """Stores a summarization result for a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='summaries'
    )
    
    # Original file info
    original_filename = models.CharField(max_length=255)
    
    # Results
    transcript = models.TextField(blank=True, default='')
    summary_text = models.TextField(blank=True, default='')
    word_count = models.IntegerField(default=0)
    target_words = models.IntegerField(default=150)
    faithfulness = models.FloatField(default=0.0)
    
    # File paths (relative to MEDIA_ROOT)
    transcript_file = models.CharField(max_length=500, blank=True, default='')
    summary_file = models.CharField(max_length=500, blank=True, default='')
    audio_file = models.CharField(max_length=500, blank=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'summaries'
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.username} ({self.created_at:%Y-%m-%d %H:%M})"
