from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg
from .models import (
    StepsRecord, SleepRecord, DietRecord, 
    RunningRecord, TrainingRecord, MoodRecord, WeightRecord, HealthGoal
)
from .forms import (
    StepsRecordForm, SleepRecordForm, DietRecordForm,
    RunningRecordForm, TrainingRecordForm, MoodRecordForm, WeightRecordForm, HealthGoalForm
)
import json
from datetime import datetime, timedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import csv
from io import StringIO
from django.contrib import messages

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
        
    try:
        weight_record = WeightRecord.objects.filter(user=request.user, date=today).latest('created_at')
    except WeightRecord.DoesNotExist:
        weight_record = None
    
    # Get user's health goals
    try:
        health_goal = HealthGoal.objects.get(user=request.user)
    except HealthGoal.DoesNotExist:
        health_goal = None
    
    context = {
        'steps_record': steps_record,
        'sleep_record': sleep_record,
        'diet_record': diet_record,
        'running_record': running_record,
        'training_record': training_record,
        'mood_record': mood_record,
        'weight_record': weight_record,
        'health_goal': health_goal,
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
            return redirect('steps_history')
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
            return redirect('steps_history')
    else:
        form = StepsRecordForm(instance=steps_record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Steps',
        'action': 'Edit'
    })

@login_required
def steps_record_history(request):
    # Get all step records, ordered by date in descending order
    all_records = StepsRecord.objects.filter(user=request.user).order_by('-date')
    
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    chart_type = request.GET.get('chart_type', 'line')
    
    # Apply date filters (if any)
    records = all_records
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass
            
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate average and maximum steps
    avg_steps = 0
    max_steps = 0
    
    if records.exists():
        steps_sum = 0
        for record in records:
            steps_sum += record.steps_count
            if record.steps_count > max_steps:
                max_steps = record.steps_count
        
        avg_steps = round(steps_sum / records.count())
    
    # Get chart data
    # Default to show last 30 days, but use filtered data if filters are applied
    if date_from or date_to:
        # Use already filtered records
        chart_records = records.order_by('date')
    else:
        # Default to show last 30 days data
        last_30_days = timezone.now().date() - timedelta(days=30)
        chart_records = all_records.filter(date__gte=last_30_days).order_by('date')
    
    # Prepare chart data
    dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
    steps = [record.steps_count for record in chart_records]
    
    # Add debugging information
    print(f"Steps chart data: {len(dates)} records found")
    for i, (date, step) in enumerate(zip(dates, steps)):
        print(f"  {i+1}: {date} - {step} steps")
    
    context = {
        'records': records,
        'record_type': 'Steps',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(steps),
        'active_tab': 'step',
        'avg_steps': avg_steps,
        'max_steps': max_steps,
        'date_from': date_from,
        'date_to': date_to,
        'chart_type': chart_type
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
            return redirect('sleep_history')
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
            return redirect('sleep_history')
    else:
        form = SleepRecordForm(instance=sleep_record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Sleep',
        'action': 'Edit'
    })

@login_required
def sleep_record_history(request):
    # Get all sleep records, ordered by date in descending order
    all_records = SleepRecord.objects.filter(user=request.user).order_by('-date')
    
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    chart_type = request.GET.get('chart_type', 'line')
    
    # Apply date filters (if any)
    records = all_records
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass
            
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate average sleep duration and quality
    avg_sleep = 0
    avg_quality = "N/A"
    quality_counts = {"poor": 0, "fair": 0, "good": 0, "excellent": 0}
    
    if records.exists():
        sleep_minutes_sum = 0
        quality_records = 0
        
        for record in records:
            sleep_minutes = record.hours * 60 + record.minutes
            sleep_minutes_sum += sleep_minutes
            if record.quality:
                quality_counts[record.quality] += 1
                quality_records += 1
        
        # Calculate average sleep duration (hours)
        avg_sleep = round(sleep_minutes_sum / (records.count() * 60), 1)
        
        # Determine most common sleep quality
        most_common_quality = "good"
        most_common_count = 0
        for quality, count in quality_counts.items():
            if count > most_common_count:
                most_common_count = count
                most_common_quality = quality
        
        if quality_records > 0:
            avg_quality = most_common_quality.title()
    
    # Get chart data
    # Default to show last 30 days, but use filtered data if filters are applied
    if date_from or date_to:
        # Use already filtered records
        chart_records = records.order_by('date')
    else:
        # Default to show last 30 days data
        last_30_days = timezone.now().date() - timedelta(days=30)
        chart_records = all_records.filter(date__gte=last_30_days).order_by('date')
    
    dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
    hours = [record.hours + (record.minutes / 60) for record in chart_records]
    
    context = {
        'records': records,
        'record_type': 'Sleep',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(hours),
        'active_tab': 'sleep',
        'avg_sleep': avg_sleep,
        'avg_quality': avg_quality,
        'date_from': date_from,
        'date_to': date_to,
        'chart_type': chart_type
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
            return redirect('diet_history')
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
            return redirect('diet_history')
    else:
        form = DietRecordForm(instance=diet_record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Diet',
        'action': 'Edit'
    })

@login_required
def diet_record_history(request):
    # Get all diet records, ordered by date in descending order
    all_records = DietRecord.objects.filter(user=request.user).order_by('-date')
    
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    chart_type = request.GET.get('chart_type', 'line')
    
    # Apply date filters (if any)
    records = all_records
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass
            
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate average calories and protein
    avg_calories = 0
    avg_protein = 0
    
    if records.exists():
        calories_sum = 0
        protein_sum = 0
        protein_records = 0
        
        for record in records:
            calories_sum += record.calories
            if record.protein:
                protein_sum += record.protein
                protein_records += 1
        
        avg_calories = round(calories_sum / records.count())
        if protein_records > 0:
            avg_protein = round(protein_sum / protein_records, 1)
    
    # Get chart data
    # Default to show last 30 days, but use filtered data if filters are applied
    if date_from or date_to:
        # Use already filtered records
        chart_records = records.order_by('date')
    else:
        # Default to show last 30 days data
        last_30_days = timezone.now().date() - timedelta(days=30)
        chart_records = all_records.filter(date__gte=last_30_days).order_by('date')
    
    dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
    calories = [record.calories for record in chart_records]
    
    context = {
        'records': records,
        'record_type': 'Diet',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(calories),
        'active_tab': 'diet',
        'avg_calories': avg_calories,
        'avg_protein': avg_protein,
        'date_from': date_from,
        'date_to': date_to,
        'chart_type': chart_type
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
            return redirect('running_history')
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
    # 获取所有跑步记录，按日期倒序排列
    all_records = RunningRecord.objects.filter(user=request.user).order_by('-date')
    
    # 获取过滤参数
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    chart_type = request.GET.get('chart_type', 'line')
    
    # 应用日期过滤（如有）
    records = all_records
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass
            
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # 计算总距离和平均配速
    total_distance = 0
    total_duration = 0
    avg_pace = 0
    
    for record in records:
        if record.distance:
            total_distance += float(record.distance)
        if record.duration_minutes:
            total_duration += record.duration_minutes
    
    # 计算平均配速（每公里分钟数）
    if total_distance > 0:
        avg_pace = round(total_duration / total_distance, 1)
    
    # 格式化总距离
    total_distance = round(total_distance, 1)
    
    # 获取图表数据
    # 默认显示最近30天，但如果有过滤条件则使用过滤后的数据
    if date_from or date_to:
        # 使用已过滤的记录
        chart_records = records.order_by('date')
    else:
        # 默认显示最近30天数据
        last_30_days = timezone.now().date() - timedelta(days=30)
        chart_records = all_records.filter(date__gte=last_30_days).order_by('date')
    
    dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
    distances = [float(record.distance) for record in chart_records]
    
    context = {
        'records': records,
        'record_type': 'Running',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(distances),
        'active_tab': 'running',
        'total_distance': total_distance,
        'avg_pace': avg_pace,
        'date_from': date_from,
        'date_to': date_to,
        'chart_type': chart_type
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
            return redirect('training_history')
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
    training_record = get_object_or_404(TrainingRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST, instance=training_record)
        if form.is_valid():
            form.save()
            return redirect('training_history')
    else:
        form = TrainingRecordForm(instance=training_record)
    
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
    # 获取所有训练记录，按日期倒序排列
    all_records = TrainingRecord.objects.filter(user=request.user).order_by('-date')
    
    # 获取过滤参数
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    chart_type = request.GET.get('chart_type', 'line')
    
    # 应用日期过滤（如有）
    records = all_records
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass
            
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # 计算训练统计信息
    total_duration = 0
    exercise_types = {}
    
    for record in records:
        if record.duration_minutes:
            total_duration += record.duration_minutes
        if record.exercise_type:
            exercise_types[record.exercise_type] = exercise_types.get(record.exercise_type, 0) + 1
    
    # Find most common training type
    most_common_exercise = max(exercise_types.items(), key=lambda x: x[1])[0] if exercise_types else "Unknown"
    
    # Format total training time to hours and minutes
    hours = total_duration // 60
    minutes = total_duration % 60
    total_training_time = f"{hours} hours {minutes} minutes" if hours > 0 else f"{minutes} minutes"
    
    # Pagination
    paginator = Paginator(records, 10)
    page = request.GET.get('page')
    
    try:
        paginated_records = paginator.page(page)
    except PageNotAnInteger:
        paginated_records = paginator.page(1)
    except EmptyPage:
        paginated_records = paginator.page(paginator.num_pages)
    
    # Get chart data
    # Default to show last 30 days, but use filtered data if filters are applied
    if date_from or date_to:
        # Use already filtered records
        chart_records = all_records.filter(id__in=[r.id for r in paginated_records.object_list])
    else:
        # Default to show last 30 days data
        last_30_days = timezone.now().date() - timedelta(days=30)
        chart_records = all_records.filter(date__gte=last_30_days).order_by('date')
    
    # Group training time by exercise type
    training_data = {}
    for record in chart_records:
        date_str = record.date.strftime('%Y-%m-%d')
        if date_str not in training_data:
            training_data[date_str] = {}
        
        exercise_type = record.exercise_type or 'Other'
        if exercise_type not in training_data[date_str]:
            training_data[date_str][exercise_type] = 0
            
        if record.duration_minutes:
            training_data[date_str][exercise_type] += record.duration_minutes
    
    # Prepare chart data
    all_exercise_types = set()
    for date_data in training_data.values():
        all_exercise_types.update(date_data.keys())
    
    dates = sorted(training_data.keys())
    exercise_data = {}
    
    for exercise_type in all_exercise_types:
        exercise_data[exercise_type] = [training_data.get(date, {}).get(exercise_type, 0) for date in dates]
    
    return render(request, 'health/training_history.html', {
        'training_records': paginated_records,
        'most_common_exercise': most_common_exercise,
        'total_training_time': total_training_time,
        'chart_dates': json.dumps(dates),
        'exercise_data': json.dumps(exercise_data),
        'exercise_types': json.dumps(list(all_exercise_types)),
        'active_tab': 'training',
        'date_from': date_from,
        'date_to': date_to,
        'chart_type': chart_type
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
            return redirect('mood_history')
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
    """Render mood record history page"""
    # 获取所有心情记录，按日期倒序排列
    all_records = MoodRecord.objects.filter(user=request.user).order_by('-date')
    
    # 获取过滤参数
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # 应用日期过滤（如有）
    records = all_records
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass
            
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # 计算情绪统计
    mood_stats = {
        'terrible': 0,
        'bad': 0,
        'neutral': 0,
        'good': 0, 
        'excellent': 0
    }
    
    for record in records:
        if record.mood in mood_stats:
            mood_stats[record.mood] += 1
    
    # Find most common mood
    most_common_mood = max(mood_stats.items(), key=lambda x: x[1])[0] if any(mood_stats.values()) else "Unknown"
    
    # Pagination
    paginator = Paginator(records, 10)
    page = request.GET.get('page')
    
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)
    
    context = {
        'records': records,
        'most_common_mood': most_common_mood.title(),
        'mood_stats': mood_stats,
        'active_tab': 'mood',
        'date_from': date_from,
        'date_to': date_to
    }
        
    return render(request, 'health/mood_record_history.html', context)

# Weight Record Views
@login_required
def weight_record_add(request):
    """Add a new weight record"""
    if request.method == 'POST':
        form = WeightRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('weight_history')
    else:
        form = WeightRecordForm()
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Weight',
        'action': 'Add'
    })

@login_required
def weight_record_edit(request, pk):
    """Edit an existing weight record"""
    record = get_object_or_404(WeightRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = WeightRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('weight_history')
    else:
        form = WeightRecordForm(instance=record)
    
    return render(request, 'health/record_form.html', {
        'form': form,
        'record_type': 'Weight',
        'action': 'Edit'
    })

@login_required
def weight_record_delete(request, pk):
    """Delete a weight record"""
    record = get_object_or_404(WeightRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        record.delete()
        return redirect('weight_history')
    
    return render(request, 'health/record_confirm_delete.html', {
        'record': record,
        'record_type': 'Weight'
    })

@login_required
def weight_record_history(request):
    """View weight history"""
    # 获取所有体重记录，按日期倒序排列
    all_records = WeightRecord.objects.filter(user=request.user).order_by('-date')
    
    # 获取过滤参数
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    chart_type = request.GET.get('chart_type', 'line')
    
    # 应用日期过滤（如有）
    records = all_records
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            pass
            
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # 计算平均体重和BMI
    avg_weight = records.aggregate(Avg('weight'))['weight__avg']
    if avg_weight:
        avg_weight = round(avg_weight, 1)
    
    # 计算平均BMI
    bmi_sum = 0
    bmi_count = 0
    for record in records:
        bmi = record.bmi()
        if bmi > 0:
            bmi_sum += bmi
            bmi_count += 1
    
    avg_bmi = round(bmi_sum / bmi_count, 1) if bmi_count > 0 else 0
    
    # Pagination
    paginator = Paginator(records, 10)  # Show 10 records per page
    page = request.GET.get('page')
    try:
        paginated_records = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        paginated_records = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        paginated_records = paginator.page(paginator.num_pages)
    
    # Get chart data
    # Default to show last 30 days, but use filtered data if filters are applied
    if date_from or date_to:
        # Use complete filtered record set, not paginated records
        chart_records = records.order_by('date')
    else:
        # Default to show last 30 days data
        last_30_days = timezone.now().date() - timedelta(days=30)
        chart_records = all_records.filter(date__gte=last_30_days).order_by('date')
    
    # Prepare chart data
    dates = [record.date.strftime('%Y-%m-%d') for record in chart_records]
    weights = [float(record.weight) for record in chart_records]
    bmis = [float(record.bmi()) for record in chart_records]
    
    context = {
        'records': paginated_records,
        'record_type': 'Weight',
        'chart_dates': json.dumps(dates),
        'chart_data': json.dumps(weights),
        'chart_bmi_data': json.dumps(bmis),
        'active_tab': 'weight',
        'avg_weight': avg_weight,
        'avg_bmi': avg_bmi,
        'date_from': date_from,
        'date_to': date_to,
        'chart_type': chart_type
    }
    
    return render(request, 'health/record_history.html', context)

# Health Goal Views
@login_required
def health_goal_edit(request):
    """Create or edit health goals"""
    # Get or create the user's health goal
    goal, created = HealthGoal.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = HealthGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = HealthGoalForm(instance=goal)
    
    return render(request, 'health/health_goal_form.html', {
        'form': form,
        'action': 'Edit' if not created else 'Create'
    })

@login_required
def export_health_data(request):
    """Export all health data as CSV format"""
    # Create response object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="welllog_health_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header information - user details and export date
    writer.writerow(['WellLog Health Data Export'])
    writer.writerow([f'User: {request.user.username}'])
    writer.writerow([f'Export Date: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([])  # Empty line to separate

    # Export steps records
    writer.writerow(['STEPS RECORDS'])
    writer.writerow(['Date', 'Steps Count', 'Created At'])
    steps_records = StepsRecord.objects.filter(user=request.user).order_by('date')
    for record in steps_records:
        writer.writerow([
            record.date.strftime('%Y-%m-%d'),
            record.steps_count,
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    writer.writerow([])  # Empty line to separate
    
    # Export sleep records
    writer.writerow(['SLEEP RECORDS'])
    writer.writerow(['Date', 'Hours', 'Minutes', 'Quality', 'Created At'])
    sleep_records = SleepRecord.objects.filter(user=request.user).order_by('date')
    for record in sleep_records:
        writer.writerow([
            record.date.strftime('%Y-%m-%d'),
            record.hours,
            record.minutes,
            record.quality,
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    writer.writerow([])  # Empty line to separate
    
    # Export diet records
    writer.writerow(['DIET RECORDS'])
    writer.writerow(['Date', 'Calories', 'Protein', 'Carbs', 'Fat', 'Notes', 'Created At'])
    diet_records = DietRecord.objects.filter(user=request.user).order_by('date')
    for record in diet_records:
        writer.writerow([
            record.date.strftime('%Y-%m-%d'),
            record.calories,
            record.protein if record.protein else '',
            record.carbs if record.carbs else '',
            record.fat if record.fat else '',
            record.notes.replace('\n', ' ') if record.notes else '',
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    writer.writerow([])  # Empty line to separate
    
    # Export running records
    writer.writerow(['RUNNING RECORDS'])
    writer.writerow(['Date', 'Distance', 'Duration Minutes', 'Calories Burned', 'Created At'])
    running_records = RunningRecord.objects.filter(user=request.user).order_by('date')
    for record in running_records:
        writer.writerow([
            record.date.strftime('%Y-%m-%d'),
            record.distance,
            record.duration_minutes,
            record.calories_burned if record.calories_burned else '',
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    writer.writerow([])  # Empty line to separate
    
    # Export training records
    writer.writerow(['TRAINING RECORDS'])
    writer.writerow(['Date', 'Exercise Type', 'Sets', 'Reps', 'Weight', 'Duration Minutes', 'Calories Burned', 'Notes', 'Created At'])
    training_records = TrainingRecord.objects.filter(user=request.user).order_by('date')
    for record in training_records:
        writer.writerow([
            record.date.strftime('%Y-%m-%d'),
            record.exercise_type,
            record.sets if record.sets else '',
            record.reps if record.reps else '',
            record.weight if record.weight else '',
            record.duration_minutes if record.duration_minutes else '',
            record.calories_burned if record.calories_burned else '',
            record.notes.replace('\n', ' ') if record.notes else '',
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    writer.writerow([])  # Empty line to separate
    
    # Export mood records
    writer.writerow(['MOOD RECORDS'])
    writer.writerow(['Date', 'Mood', 'Stress Level', 'Notes', 'Created At'])
    mood_records = MoodRecord.objects.filter(user=request.user).order_by('date')
    for record in mood_records:
        writer.writerow([
            record.date.strftime('%Y-%m-%d'),
            record.mood,
            record.stress_level if record.stress_level else '',
            record.notes.replace('\n', ' ') if record.notes else '',
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    writer.writerow([])  # Empty line to separate
    
    # Export weight records
    writer.writerow(['WEIGHT RECORDS'])
    writer.writerow(['Date', 'Weight', 'Height', 'BMI', 'Notes', 'Created At'])
    weight_records = WeightRecord.objects.filter(user=request.user).order_by('date')
    for record in weight_records:
        writer.writerow([
            record.date.strftime('%Y-%m-%d'),
            record.weight,
            record.height,
            record.bmi(),
            record.notes.replace('\n', ' ') if record.notes else '',
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
def import_health_data(request):
    """Import health data from CSV format"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check file type
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV format file')
            return redirect('dashboard')
        
        # Process CSV file
        try:
            # Decode CSV file
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.reader(StringIO(decoded_file))
            
            # Record import statistics
            stats = {
                'steps': 0,
                'sleep': 0,
                'diet': 0,
                'running': 0,
                'training': 0,
                'mood': 0,
                'weight': 0,
                'errors': 0
            }
            
            # Parse CSV data
            current_section = None
            headers = None
            
            for row in csv_data:
                # Skip empty lines
                if not row or not any(row):
                    continue
                
                # Check if it's a partial header line
                if len(row) == 1 and row[0].endswith('RECORDS'):
                    current_section = row[0].split()[0].lower()
                    headers = None
                    continue
                
                # If it's a header line, save header
                if current_section and not headers and 'date' in row[0].lower():
                    headers = row
                    continue
                
                # If there's a header line and current section, process data line
                if current_section and headers:
                    try:
                        if current_section == 'steps':
                            # Process steps record
                            date_str = row[0]
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            steps_count = int(row[1])
                            
                            # Create or update record
                            record, created = StepsRecord.objects.update_or_create(
                                user=request.user,
                                date=date,
                                defaults={
                                    'steps_count': steps_count
                                }
                            )
                            stats['steps'] += 1
                            
                        elif current_section == 'sleep':
                            # Process sleep record
                            date_str = row[0]
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            hours = int(row[1])
                            minutes = int(row[2])
                            quality = row[3] if row[3] else None
                            
                            # Create or update record
                            record, created = SleepRecord.objects.update_or_create(
                                user=request.user,
                                date=date,
                                defaults={
                                    'hours': hours,
                                    'minutes': minutes,
                                    'quality': quality
                                }
                            )
                            stats['sleep'] += 1
                            
                        elif current_section == 'diet':
                            # Process diet record
                            date_str = row[0]
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            calories = int(row[1])
                            protein = float(row[2]) if row[2] else None
                            carbs = float(row[3]) if row[3] else None
                            fat = float(row[4]) if row[4] else None
                            notes = row[5] if len(row) > 5 and row[5] else None
                            
                            # Create or update record
                            record, created = DietRecord.objects.update_or_create(
                                user=request.user,
                                date=date,
                                defaults={
                                    'calories': calories,
                                    'protein': protein,
                                    'carbs': carbs,
                                    'fat': fat,
                                    'notes': notes
                                }
                            )
                            stats['diet'] += 1
                            
                        elif current_section == 'running':
                            # Process running record
                            date_str = row[0]
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            distance = float(row[1])
                            duration_minutes = int(row[2])
                            calories_burned = int(row[3]) if row[3] else None
                            
                            # Create or update record
                            record, created = RunningRecord.objects.update_or_create(
                                user=request.user,
                                date=date,
                                defaults={
                                    'distance': distance,
                                    'duration_minutes': duration_minutes,
                                    'calories_burned': calories_burned
                                }
                            )
                            stats['running'] += 1
                            
                        elif current_section == 'training':
                            # Process training record
                            date_str = row[0]
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            exercise_type = row[1]
                            sets = int(row[2]) if row[2] else None
                            reps = int(row[3]) if row[3] else None
                            weight = float(row[4]) if row[4] else None
                            duration_minutes = int(row[5]) if row[5] else None
                            calories_burned = int(row[6]) if row[6] else None
                            notes = row[7] if len(row) > 7 and row[7] else None
                            
                            # Create new record (because a day may have multiple trainings)
                            record = TrainingRecord.objects.create(
                                user=request.user,
                                date=date,
                                exercise_type=exercise_type,
                                sets=sets,
                                reps=reps,
                                weight=weight,
                                duration_minutes=duration_minutes,
                                calories_burned=calories_burned,
                                notes=notes
                            )
                            stats['training'] += 1
                            
                        elif current_section == 'mood':
                            # Process mood record
                            date_str = row[0]
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            mood = row[1]
                            stress_level = int(row[2]) if row[2] else None
                            notes = row[3] if len(row) > 3 and row[3] else None
                            
                            # Create or update record
                            record, created = MoodRecord.objects.update_or_create(
                                user=request.user,
                                date=date,
                                defaults={
                                    'mood': mood,
                                    'stress_level': stress_level,
                                    'notes': notes
                                }
                            )
                            stats['mood'] += 1
                            
                        elif current_section == 'weight':
                            # Process weight record
                            date_str = row[0]
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            weight = float(row[1])
                            height = float(row[2])
                            notes = row[4] if len(row) > 4 and row[4] else None
                            
                            # Create or update record
                            record, created = WeightRecord.objects.update_or_create(
                                user=request.user,
                                date=date,
                                defaults={
                                    'weight': weight,
                                    'height': height,
                                    'notes': notes
                                }
                            )
                            stats['weight'] += 1
                            
                    except (ValueError, IndexError) as e:
                        stats['errors'] += 1
                        print(f"Error importing row: {row}, Error: {e}")
            
            # Generate import success message
            success_message = (f"Import successful: {stats['steps']} steps records, {stats['sleep']} sleep records, "
                               f"{stats['diet']} diet records, {stats['running']} running records, "
                               f"{stats['training']} training records, {stats['mood']} mood records, "
                               f"{stats['weight']} weight records")
            
            if stats['errors'] > 0:
                success_message += f", ignored {stats['errors']} error records"
                
            messages.success(request, success_message)
            
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
            
    return redirect('dashboard')