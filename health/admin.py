from django.contrib import admin
from .models import (
    StepsRecord, SleepRecord, DietRecord, 
    RunningRecord, TrainingRecord, MoodRecord
)

@admin.register(StepsRecord)
class StepsRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'steps_count')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__email')

@admin.register(SleepRecord)
class SleepRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'hours', 'minutes', 'quality')
    list_filter = ('date', 'user', 'quality')
    search_fields = ('user__username', 'user__email')

@admin.register(DietRecord)
class DietRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'calories', 'protein', 'carbs', 'fat')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__email')

@admin.register(RunningRecord)
class RunningRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'distance', 'duration_minutes', 'calories_burned')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__email')

@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'exercise_type', 'sets', 'reps', 'weight')
    list_filter = ('date', 'user', 'exercise_type')
    search_fields = ('user__username', 'user__email', 'exercise_type')

@admin.register(MoodRecord)
class MoodRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'mood', 'stress_level')
    list_filter = ('date', 'user', 'mood')
    search_fields = ('user__username', 'user__email')
