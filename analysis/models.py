from django.db import models
from django.conf import settings

# Create your models here.

class HealthAdvice(models.Model):
    """存储AI生成的健康建议"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(help_text="AI生成的健康建议内容")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "健康建议"
        verbose_name_plural = "健康建议"
    
    def __str__(self):
        return f"{self.user.username}的健康建议 - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
