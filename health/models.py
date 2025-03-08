from django.db import models
from django.conf import settings
from django.utils import timezone

# Base class for all health records
class HealthRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

# Steps record
class StepsRecord(HealthRecord):
    steps_count = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.steps_count} steps"

# Sleep record
class SleepRecord(HealthRecord):
    hours = models.PositiveIntegerField()
    minutes = models.PositiveIntegerField()
    quality = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('poor', 'Poor'),
        ('fair', 'Fair'),
        ('good', 'Good'),
        ('excellent', 'Excellent')
    ])
    
    def total_hours(self):
        return self.hours + (self.minutes / 60)
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.hours}h {self.minutes}min"

# Diet record
class DietRecord(HealthRecord):
    calories = models.PositiveIntegerField()
    protein = models.FloatField(blank=True, null=True)  # grams
    carbs = models.FloatField(blank=True, null=True)    # grams
    fat = models.FloatField(blank=True, null=True)      # grams
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.calories} kcal"

# Running record
class RunningRecord(HealthRecord):
    distance = models.FloatField()  # kilometers
    duration_minutes = models.PositiveIntegerField()
    calories_burned = models.PositiveIntegerField(blank=True, null=True)
    
    def pace(self):
        if self.distance > 0:
            minutes_per_km = self.duration_minutes / self.distance
            whole_minutes = int(minutes_per_km)
            seconds = int((minutes_per_km - whole_minutes) * 60)
            return f"{whole_minutes}:{seconds:02d} min/km"
        return "0:00 min/km"
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.distance} km"

# Training record
class TrainingRecord(HealthRecord):
    exercise_type = models.CharField(max_length=100)
    sets = models.PositiveIntegerField(blank=True, null=True)
    reps = models.PositiveIntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)  # kg
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    calories_burned = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.exercise_type}"

# Mood record
class MoodRecord(HealthRecord):
    mood = models.CharField(max_length=20, choices=[
        ('terrible', 'Terrible'),
        ('bad', 'Bad'),
        ('neutral', 'Neutral'),
        ('good', 'Good'),
        ('excellent', 'Excellent')
    ])
    stress_level = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 11)], blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.mood}"

# Weight record
class WeightRecord(HealthRecord):
    weight = models.FloatField()  # kg
    height = models.FloatField()  # cm
    notes = models.TextField(blank=True, null=True)
    
    def bmi(self):
        """Calculate Body Mass Index (BMI)"""
        if self.height > 0:
            # Convert height from cm to m and calculate BMI
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters * height_in_meters), 2)
        return 0
    
    def bmi_category(self):
        """Return the BMI category based on calculated BMI"""
        bmi_value = self.bmi()
        if bmi_value < 18.5:
            return "Underweight"
        elif bmi_value < 25:
            return "Normal weight"
        elif bmi_value < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.weight} kg (BMI: {self.bmi()})"

# Health goal
class HealthGoal(models.Model):
    """Model for storing health and fitness goals"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Weight goals
    target_weight = models.FloatField(blank=True, null=True, help_text="Target weight in kg")
    weight_goal_date = models.DateField(blank=True, null=True, help_text="Target date to achieve weight goal")
    
    # Steps goals
    daily_steps_goal = models.PositiveIntegerField(blank=True, null=True, help_text="Daily steps goal")
    
    # Sleep goals
    daily_sleep_hours_goal = models.PositiveIntegerField(blank=True, null=True, help_text="Daily sleep hours goal")
    daily_sleep_minutes_goal = models.PositiveIntegerField(blank=True, null=True, default=0, help_text="Additional minutes for sleep goal")
    
    # Running goals
    weekly_running_distance_goal = models.FloatField(blank=True, null=True, help_text="Weekly running distance goal in km")
    weekly_running_sessions_goal = models.PositiveIntegerField(blank=True, null=True, help_text="Number of running sessions per week")
    
    # Training goals
    weekly_training_sessions_goal = models.PositiveIntegerField(blank=True, null=True, help_text="Number of training sessions per week")
    
    # Diet goals
    daily_calories_goal = models.PositiveIntegerField(blank=True, null=True, help_text="Daily calories intake goal")
    daily_protein_goal = models.FloatField(blank=True, null=True, help_text="Daily protein intake goal in grams")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Health Goals"
    
    class Meta:
        verbose_name = "Health Goal"
        verbose_name_plural = "Health Goals"