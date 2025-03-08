from django.db import models
from django.conf import settings

# Create your models here.

class HealthAdvice(models.Model):
    """Store AI-generated health advice"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(help_text="AI-generated health advice content")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Health Advice"
        verbose_name_plural = "Health Advice"
    
    def __str__(self):
        return f"{self.user.username}'s Health Advice - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
