from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Sum, Avg
from .models import (
    StepsRecord, SleepRecord, DietRecord, 
    RunningRecord, TrainingRecord, MoodRecord
)
from .forms import (
    StepsRecordForm, SleepRecordForm, DietRecordForm,
    RunningRecordForm, TrainingRecordForm, MoodRecordForm
)
import json
from datetime import datetime, timedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

@login_required
def dashboard(request):
    """Main dashboard view showing today's health data"""
    today = timezone.now().date()
    
    # Get today's records for each health type
    try:
        steps_record = StepsRecord.objects.filter(user=request.user, date=today).latest('created_at')
    except StepsRecord.DoesNotExist:
        steps_record = None
        
    try:
        sleep_record = SleepRecord.objects.filter(user=request.user, date=today).latest('created_at')
    except SleepRecord.DoesNotExist:
        sleep_record = None
        
    try:
        diet_record = DietRecord.objects.filter(user=request.user, date=today).latest('created_at')
    except DietRecord.DoesNotExist:
        diet_record = None
    
    try:
        running_record = RunningRecord.objects.filter(user=request.user, date=today).latest('created_at')
    except RunningRecord.DoesNotExist:
        running_record = None
        
    try:
        training_record = TrainingRecord.objects.filter(user=request.user, date=today).latest('created_at')
    except TrainingRecord.DoesNotExist:
        training_record = None
        
    try:
        mood_record = MoodRecord.objects.filter(user=request.user, date=today).latest('created_at')
    except MoodRecord.DoesNotExist:
        mood_record = None
    
    context = {
        'steps_record': steps_record,
        'sleep_record': sleep_record,
        'diet_record': diet_record,
        'running_record': running_record,
        'training_record': training_record,
        'mood_record': mood_record,
        'active_tab': 'overall'
    }
    
    return render(request, 'health/dashboard.html', context)

# Steps Record Views
@login_required
def steps_record_add(request):
    if request.method == 'POST':
        form = StepsRecordForm(request.POST)
        if form.is_valid():
            steps_record = form.save(commit=False)
            steps_record.user = request.user
            steps_record.save()
            return redirect('dashboard')
    else:
        form = StepsRecordForm(initial={'date': timezone.now().date()})
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Steps',
        'action': 'Add'
    })

@login_required
def steps_record_edit(request, pk):
    steps_record = get_object_or_404(StepsRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = StepsRecordForm(request.POST, instance=steps_record)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = StepsRecordForm(instance=steps_record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Steps',
        'action': 'Edit'
    })

@login_required
def steps_record_history(request):
    records = StepsRecord.objects.filter(user=request.user).order_by('-date')
    
    # Get data for chart - last 30 days
    last_30_days = timezone.now().date() - timedelta(days=30)
    
    # 直接获取每天的步数，不使用Sum聚合
    chart_records = StepsRecord.objects.filter(
        user=request.user, 
        date__gte=last_30_days
    ).order_by('date')
    
    # 确保有记录
    if chart_records.exists():
        # 简化数据处理逻辑
        dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
        steps = [record.steps_count for record in chart_records]
    else:
        # 无数据时设置为空列表
        dates = []
        steps = []
    
    # 添加调试信息
    print(f"Steps chart data: {len(dates)} records found")
    for i, (date, step) in enumerate(zip(dates, steps)):
        print(f"  {i+1}: {date} - {step} steps")
    
    context = {
        'records': records,
        'record_type': 'Steps',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(steps),
        'active_tab': 'step'
    }
    
    return render(request, 'health/record_history.html', context)

@login_required
def steps_record_delete(request, pk):
    steps_record = get_object_or_404(StepsRecord, pk=pk, user=request.user)
    if request.method == 'POST':
        steps_record.delete()
        return redirect('steps_history')
    return render(request, 'health/record_confirm_delete.html', {
        'record': steps_record,
        'record_type': 'Steps'
    })

# Sleep Record Views
@login_required
def sleep_record_add(request):
    if request.method == 'POST':
        form = SleepRecordForm(request.POST)
        if form.is_valid():
            sleep_record = form.save(commit=False)
            sleep_record.user = request.user
            sleep_record.save()
            return redirect('dashboard')
    else:
        form = SleepRecordForm(initial={'date': timezone.now().date()})
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Sleep',
        'action': 'Add'
    })

@login_required
def sleep_record_edit(request, pk):
    sleep_record = get_object_or_404(SleepRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = SleepRecordForm(request.POST, instance=sleep_record)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SleepRecordForm(instance=sleep_record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Sleep',
        'action': 'Edit'
    })

@login_required
def sleep_record_history(request):
    records = SleepRecord.objects.filter(user=request.user).order_by('-date')
    
    # Get data for chart
    last_30_days = timezone.now().date() - timedelta(days=30)
    chart_records = SleepRecord.objects.filter(
        user=request.user, 
        date__gte=last_30_days
    ).order_by('date')
    
    dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
    hours = [record.hours + (record.minutes / 60) for record in chart_records]
    
    context = {
        'records': records,
        'record_type': 'Sleep',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(hours),
        'active_tab': 'sleep'
    }
    
    return render(request, 'health/record_history.html', context)

@login_required
def sleep_record_delete(request, pk):
    sleep_record = get_object_or_404(SleepRecord, pk=pk, user=request.user)
    if request.method == 'POST':
        sleep_record.delete()
        return redirect('sleep_history')
    return render(request, 'health/record_confirm_delete.html', {
        'record': sleep_record,
        'record_type': 'Sleep'
    })

# Diet Record Views
@login_required
def diet_record_add(request):
    if request.method == 'POST':
        form = DietRecordForm(request.POST)
        if form.is_valid():
            diet_record = form.save(commit=False)
            diet_record.user = request.user
            diet_record.save()
            return redirect('dashboard')
    else:
        form = DietRecordForm(initial={'date': timezone.now().date()})
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Diet',
        'action': 'Add'
    })

@login_required
def diet_record_edit(request, pk):
    diet_record = get_object_or_404(DietRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = DietRecordForm(request.POST, instance=diet_record)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = DietRecordForm(instance=diet_record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Diet',
        'action': 'Edit'
    })

@login_required
def diet_record_history(request):
    records = DietRecord.objects.filter(user=request.user).order_by('-date')
    
    # Get data for chart
    last_30_days = timezone.now().date() - timedelta(days=30)
    chart_records = DietRecord.objects.filter(
        user=request.user, 
        date__gte=last_30_days
    ).order_by('date')
    
    dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
    calories = [record.calories for record in chart_records]
    
    context = {
        'records': records,
        'record_type': 'Diet',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(calories),
        'active_tab': 'diet'
    }
    
    return render(request, 'health/record_history.html', context)

@login_required
def diet_record_delete(request, pk):
    diet_record = get_object_or_404(DietRecord, pk=pk, user=request.user)
    if request.method == 'POST':
        diet_record.delete()
        return redirect('diet_history')
    return render(request, 'health/record_confirm_delete.html', {
        'record': diet_record,
        'record_type': 'Diet'
    })

# Running Record Views
@login_required
def running_record_add(request):
    """Add a new running record"""
    if request.method == 'POST':
        form = RunningRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('dashboard')
    else:
        form = RunningRecordForm()
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Running',
        'action': 'Add'
    })

@login_required
def running_record_edit(request, pk):
    """Edit an existing running record"""
    record = get_object_or_404(RunningRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = RunningRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('running_history')
    else:
        form = RunningRecordForm(instance=record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Running',
        'action': 'Edit'
    })

@login_required
def running_record_delete(request, pk):
    """Delete a running record"""
    record = get_object_or_404(RunningRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        record.delete()
        return redirect('running_history')
    
    return render(request, 'health/record_confirm_delete.html', {
        'record': record,
        'record_type': 'Running'
    })

@login_required
def running_record_history(request):
    """View running history"""
    records = RunningRecord.objects.filter(user=request.user).order_by('-date')
    
    # Get data for chart
    last_30_days = timezone.now().date() - timedelta(days=30)
    chart_records = RunningRecord.objects.filter(
        user=request.user, 
        date__gte=last_30_days
    ).order_by('date')
    
    dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
    distances = [float(record.distance) for record in chart_records]
    
    context = {
        'records': records,
        'record_type': 'Running',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(distances),
        'active_tab': 'running'
    }
    
    return render(request, 'health/record_history.html', context)

# Training Record Views
@login_required
def training_record_add(request):
    """Add a new training record"""
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST)
        if form.is_valid():
            training_record = form.save(commit=False)
            training_record.user = request.user
            training_record.save()
            return redirect('dashboard')
    else:
        form = TrainingRecordForm(initial={'date': timezone.now().date()})
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Training',
        'action': 'Add'
    })

@login_required
def training_record_edit(request, pk):
    """Edit an existing training record"""
    record = get_object_or_404(TrainingRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('training_history')
    else:
        form = TrainingRecordForm(instance=record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Training',
        'action': 'Edit'
    })

@login_required
def training_record_delete(request, pk):
    """Delete a training record"""
    record = get_object_or_404(TrainingRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        record.delete()
        return redirect('training_history')
    
    return render(request, 'health/record_confirm_delete.html', {
        'record': record,
        'record_type': 'Training'
    })

@login_required
def training_record_history(request):
    """View training history"""
    records = TrainingRecord.objects.filter(user=request.user).order_by('-date')
    return render(request, 'health/training_history.html', {
        'records': records,
        'active_tab': 'training'
    })

# Mood Record Views
@login_required
def mood_record_add(request):
    """Add a new mood record"""
    if request.method == 'POST':
        form = MoodRecordForm(request.POST)
        if form.is_valid():
            mood_record = form.save(commit=False)
            mood_record.user = request.user
            mood_record.save()
            return redirect('dashboard')
    else:
        form = MoodRecordForm(initial={'date': timezone.now().date()})
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Mood',
        'action': 'Add'
    })

@login_required
def mood_record_edit(request, pk):
    """Edit an existing mood record"""
    record = get_object_or_404(MoodRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = MoodRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('mood_history')
    else:
        form = MoodRecordForm(instance=record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Mood',
        'action': 'Edit'
    })

@login_required
def mood_record_delete(request, pk):
    """Delete a mood record"""
    record = get_object_or_404(MoodRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        record.delete()
        return redirect('mood_history')
    
    return render(request, 'health/record_confirm_delete.html', {
        'record': record,
        'record_type': 'Mood'
    })

@login_required
def mood_record_history(request):
    """渲染心情记录历史页面"""
    mood_records = MoodRecord.objects.filter(user=request.user).order_by('-record_date')
    
    paginator = Paginator(mood_records, 10)
    page = request.GET.get('page')
    
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)
        
    return render(request, 'health/mood_record_history.html', {'records': records})