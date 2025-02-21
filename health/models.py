from django.db import models
from django.conf import settings

class HealthRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    diet = models.CharField(max_length=255, blank=True, null=True)    
    exercise = models.CharField(max_length=255, blank=True, null=True)
    sleep_hours = models.FloatField(blank=True, null=True)            
    mood = models.CharField(max_length=50, blank=True, null=True)     

    def __str__(self):
        return f"{self.user.username} - {self.date}"