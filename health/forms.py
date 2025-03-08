from django import forms
from .models import StepsRecord, SleepRecord, DietRecord, RunningRecord, TrainingRecord, MoodRecord, WeightRecord, HealthGoal

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

class WeightRecordForm(forms.ModelForm):
    class Meta:
        model = WeightRecord
        fields = ['date', 'weight', 'height', 'notes']
        widgets = {
            'date': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'weight': 'Weight (kg)',
            'height': 'Height (cm)',
        }

class HealthGoalForm(forms.ModelForm):
    class Meta:
        model = HealthGoal
        fields = [
            'target_weight', 'weight_goal_date', 
            'daily_steps_goal', 
            'daily_sleep_hours_goal', 'daily_sleep_minutes_goal', 
            'weekly_running_distance_goal', 'weekly_running_sessions_goal',
            'weekly_training_sessions_goal',
            'daily_calories_goal', 'daily_protein_goal'
        ]
        widgets = {
            'weight_goal_date': DateInput(),
        }
        labels = {
            'target_weight': 'Target Weight (kg)',
            'weight_goal_date': 'Target Date',
            'daily_steps_goal': 'Daily Steps Goal',
            'daily_sleep_hours_goal': 'Sleep Hours Goal',
            'daily_sleep_minutes_goal': 'Sleep Minutes Goal',
            'weekly_running_distance_goal': 'Weekly Running Distance (km)',
            'weekly_running_sessions_goal': 'Weekly Running Sessions',
            'weekly_training_sessions_goal': 'Weekly Training Sessions',
            'daily_calories_goal': 'Daily Calories Goal',
            'daily_protein_goal': 'Daily Protein Goal (g)',
        } 