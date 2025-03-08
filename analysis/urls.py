from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('ai-advice/', views.ai_advice, name='ai_advice'),
    path('ai-advice/generate/', views.generate_advice, name='generate_advice'),
] 