from django import forms
from .models import StepsRecord, SleepRecord, DietRecord, RunningRecord, TrainingRecord, MoodRecord

class DateInput(forms.DateInput):
    input_type = 'date'

class StepsRecordForm(forms.ModelForm):
    class Meta:
        model = StepsRecord
        fields = ['date', 'steps_count']
        widgets = {
            'date': DateInput(),
        }
        labels = {
            'steps_count': 'Steps Count',
        }

class SleepRecordForm(forms.ModelForm):
    class Meta:
        model = SleepRecord
        fields = ['date', 'hours', 'minutes', 'quality']
        widgets = {
            'date': DateInput(),
        }
        
class DietRecordForm(forms.ModelForm):
    class Meta:
        model = DietRecord
        fields = ['date', 'calories', 'protein', 'carbs', 'fat', 'notes']
        widgets = {
            'date': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'protein': 'Protein (g)',
            'carbs': 'Carbohydrates (g)',
            'fat': 'Fat (g)',
        }

class RunningRecordForm(forms.ModelForm):
    class Meta:
        model = RunningRecord
        fields = ['date', 'distance', 'duration_minutes', 'calories_burned']
        widgets = {
            'date': DateInput(),
        }
        labels = {
            'distance': 'Distance (km)',
            'duration_minutes': 'Duration (minutes)',
            'calories_burned': 'Calories Burned',
        }

class TrainingRecordForm(forms.ModelForm):
    class Meta:
        model = TrainingRecord
        fields = ['date', 'exercise_type', 'sets', 'reps', 'weight', 'duration_minutes', 'calories_burned', 'notes']
        widgets = {
            'date': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'exercise_type': 'Exercise Type',
            'weight': 'Weight (kg)',
            'duration_minutes': 'Duration (minutes)',
            'calories_burned': 'Calories Burned',
        }

class MoodRecordForm(forms.ModelForm):
    class Meta:
        model = MoodRecord
        fields = ['date', 'mood', 'stress_level', 'notes']
        widgets = {
            'date': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'stress_level': 'Stress Level (1-10)',
        } 