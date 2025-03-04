from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Steps Records
    path('steps/add/', views.steps_record_add, name='steps_add'),
    path('steps/edit/<int:pk>/', views.steps_record_edit, name='steps_edit'),
    path('steps/delete/<int:pk>/', views.steps_record_delete, name='steps_delete'),
    path('steps/history/', views.steps_record_history, name='steps_history'),
    
    # Sleep Records
    path('sleep/add/', views.sleep_record_add, name='sleep_add'),
    path('sleep/edit/<int:pk>/', views.sleep_record_edit, name='sleep_edit'),
    path('sleep/delete/<int:pk>/', views.sleep_record_delete, name='sleep_delete'),
    path('sleep/history/', views.sleep_record_history, name='sleep_history'),
    
    # Diet Records
    path('diet/add/', views.diet_record_add, name='diet_add'),
    path('diet/edit/<int:pk>/', views.diet_record_edit, name='diet_edit'),
    path('diet/delete/<int:pk>/', views.diet_record_delete, name='diet_delete'),
    path('diet/history/', views.diet_record_history, name='diet_history'),
    
    # Running Records
    path('running/add/', views.running_record_add, name='running_add'),
    path('running/edit/<int:pk>/', views.running_record_edit, name='running_edit'),
    path('running/delete/<int:pk>/', views.running_record_delete, name='running_delete'),
    path('running/history/', views.running_record_history, name='running_history'),
    
    # Training Records
    path('training/add/', views.training_record_add, name='training_add'),
    path('training/edit/<int:pk>/', views.training_record_edit, name='training_edit'),
    path('training/delete/<int:pk>/', views.training_record_delete, name='training_delete'),
    path('training/history/', views.training_record_history, name='training_history'),
    
    # Mood Records
    path('mood/add/', views.mood_record_add, name='mood_add'),
    path('mood/edit/<int:pk>/', views.mood_record_edit, name='mood_edit'),
    path('mood/delete/<int:pk>/', views.mood_record_delete, name='mood_delete'),
    path('mood/history/', views.mood_record_history, name='mood_history'),
] 