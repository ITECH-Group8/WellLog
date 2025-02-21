from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import HealthRecord
from django.utils import timezone

@login_required
def create_health_record(request):
    if request.method == 'POST':
        date = request.POST.get('date', timezone.now().date())  # 默认为当天
        diet = request.POST.get('diet', '')
        exercise = request.POST.get('exercise', '')
        sleep_hours = request.POST.get('sleep_hours', 0)
        mood = request.POST.get('mood', '')

        HealthRecord.objects.create(
            user=request.user,
            date=date,
            diet=diet,
            exercise=exercise,
            sleep_hours=sleep_hours,
            mood=mood
        )
        return redirect('health_list')
    return render(request, 'health/create_record.html')

@login_required
def list_health_records(request):
    records = HealthRecord.objects.filter(user=request.user).order_by('-date')
    return render(request, 'health/list_records.html', {'records': records})