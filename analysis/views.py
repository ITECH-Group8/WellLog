from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json
import asyncio
from openai import AsyncOpenAI
from asgiref.sync import sync_to_async
from .models import HealthAdvice

from health.models import (
    RunningRecord, 
    StepsRecord, 
    SleepRecord, 
    DietRecord, 
    MoodRecord,
    TrainingRecord,
    HealthGoal,
    WeightRecord
)

def get_running_data(user, start_date):
    """Get running records data for a user since start_date"""
    return list(RunningRecord.objects.filter(
        user=user, 
        date__gte=start_date
    ).order_by('-date').values('id', 'date', 'distance', 'duration_minutes', 'calories_burned'))

def get_sleep_data(user, start_date):
    """Get sleep records data for a user since start_date"""
    return list(SleepRecord.objects.filter(
        user=user, 
        date__gte=start_date
    ).order_by('-date').values('id', 'date', 'hours', 'minutes', 'quality'))

def get_steps_data(user, start_date):
    """Get steps records data for a user since start_date"""
    return list(StepsRecord.objects.filter(
        user=user, 
        date__gte=start_date
    ).order_by('-date').values('id', 'date', 'steps_count'))

def get_diet_data(user, start_date):
    """Get diet records data for a user since start_date"""
    return list(DietRecord.objects.filter(
        user=user, 
        date__gte=start_date
    ).order_by('-date').values('id', 'date', 'calories', 'protein', 'carbs', 'fat'))

def get_mood_data(user, start_date):
    """Get mood records data for a user since start_date"""
    return list(MoodRecord.objects.filter(
        user=user, 
        date__gte=start_date
    ).order_by('-date').values('id', 'date', 'mood', 'stress_level'))

def get_training_data(user, start_date):
    """Get training records data for a user since start_date"""
    return list(TrainingRecord.objects.filter(
        user=user, 
        date__gte=start_date
    ).order_by('-date').values('id', 'date', 'exercise_type', 'sets', 'reps', 'weight', 'duration_minutes'))

def get_weight_data(user, start_date):
    """Get weight records data for a user since start_date"""
    weight_records = list(WeightRecord.objects.filter(
        user=user, 
        date__gte=start_date
    ).order_by('-date').values('id', 'date', 'weight', 'height', 'notes'))
    
    # 计算BMI
    for record in weight_records:
        if record['height'] and record['weight']:
            # BMI = weight(kg) / (height(m))^2
            height_in_meters = record['height'] / 100
            record['bmi'] = round(record['weight'] / (height_in_meters * height_in_meters), 1)
    
    return weight_records

@login_required
def ai_advice(request):
    """主AI建议页面视图"""
    # 确保用户有配置文件
    try:
        profile = request.user.profile
    except Exception:
        # 如果用户没有配置文件，创建一个
        from accounts.models import Profile
        Profile.objects.create(user=request.user)
    
    # Get the last 30 days of health records for data overview
    last_30_days = timezone.now().date() - timedelta(days=30)
    
    running_records = RunningRecord.objects.filter(user=request.user, date__gte=last_30_days).order_by('-date')
    steps_records = StepsRecord.objects.filter(user=request.user, date__gte=last_30_days).order_by('-date')
    sleep_records = SleepRecord.objects.filter(user=request.user, date__gte=last_30_days).order_by('-date')
    diet_records = DietRecord.objects.filter(user=request.user, date__gte=last_30_days).order_by('-date')
    mood_records = MoodRecord.objects.filter(user=request.user, date__gte=last_30_days).order_by('-date')
    training_records = TrainingRecord.objects.filter(user=request.user, date__gte=last_30_days).order_by('-date')
    
    # 获取最新保存的健康建议
    latest_advice = HealthAdvice.objects.filter(user=request.user).first()
    
    context = {
        'running_records': running_records,
        'steps_records': steps_records,
        'sleep_records': sleep_records,
        'diet_records': diet_records,
        'mood_records': mood_records,
        'training_records': training_records,
        'latest_advice': latest_advice,
        'active_section': 'ai_advice'
    }
    
    return render(request, 'analysis/ai_advice.html', context)

@login_required
async def generate_advice_async(request):
    """异步生成健康建议"""
    if request.method != 'POST':
        return JsonResponse({'error': '只允许POST请求'}, status=405)
    
    try:
        # Get the last 30 days of health records
        last_30_days = timezone.now().date() - timedelta(days=30)
        
        # 使用sync_to_async包装同步数据库查询
        running_data = await sync_to_async(get_running_data)(request.user, last_30_days)
        sleep_data = await sync_to_async(get_sleep_data)(request.user, last_30_days)
        steps_data = await sync_to_async(get_steps_data)(request.user, last_30_days)
        diet_data = await sync_to_async(get_diet_data)(request.user, last_30_days)
        mood_data = await sync_to_async(get_mood_data)(request.user, last_30_days)
        training_data = await sync_to_async(get_training_data)(request.user, last_30_days)
        weight_data = await sync_to_async(get_weight_data)(request.user, last_30_days)
        
        # Convert date objects to strings
        for data_list in [running_data, sleep_data, steps_data, diet_data, mood_data, training_data, weight_data]:
            for item in data_list:
                if 'date' in item:
                    item['date'] = item['date'].strftime('%Y-%m-%d')
        
        # Prepare user data for the prompt
        user_data = {
            'running': running_data,
            'sleep': sleep_data,
            'steps': steps_data,
            'diet': diet_data,
            'mood': mood_data,
            'training': training_data,
            'weight_records': weight_data
        }
        
        # 计算用户数据统计值，以填充进提示词
        # 获取用户信息
        try:
            user_profile = await sync_to_async(lambda: request.user.profile)()
        except Exception:
            # 如果用户没有配置文件，创建一个
            from accounts.models import Profile
            await sync_to_async(Profile.objects.create)(user=request.user)
            user_profile = await sync_to_async(lambda: request.user.profile)()
            
        user_age = user_profile.age if hasattr(user_profile, 'age') else "未知"
        user_gender = user_profile.get_gender_display() if hasattr(user_profile, 'gender') else "未知"
        
        # 获取最近的体重记录
        latest_weight = None
        height = None
        bmi = None
        if len(user_data['weight_records']) > 0:
            latest_weight = user_data['weight_records'][0].get('weight', None)
            height = user_data['weight_records'][0].get('height', None)
            bmi = user_data['weight_records'][0].get('bmi', None)
        
        # 计算步数平均值
        avg_steps = 0
        if len(steps_data) > 0:
            avg_steps = sum(item.get('steps_count', 0) for item in steps_data) // len(steps_data)
        
        # 计算睡眠平均值
        avg_sleep_hours = 0
        if len(sleep_data) > 0:
            avg_sleep_hours = sum(item.get('hours', 0) for item in sleep_data) / len(sleep_data)
            avg_sleep_minutes = sum(item.get('minutes', 0) for item in sleep_data) / len(sleep_data)
            avg_sleep_hours += avg_sleep_minutes / 60
            avg_sleep_hours = round(avg_sleep_hours, 1)
        
        # 计算跑步数据
        avg_running_distance = 0
        avg_running_pace = 0
        running_sessions = len(running_data)
        if running_sessions > 0:
            avg_running_distance = sum(item.get('distance', 0) for item in running_data) / running_sessions
            avg_running_distance = round(avg_running_distance, 1)
            # 计算平均配速（分钟/公里）
            if sum(item.get('distance', 0) for item in running_data) > 0:
                total_minutes = sum(item.get('duration_minutes', 0) for item in running_data)
                total_distance = sum(item.get('distance', 0) for item in running_data)
                avg_running_pace = total_minutes / total_distance
                avg_running_pace = round(avg_running_pace, 1)
        
        # 计算饮食数据
        avg_calories = 0
        avg_protein = 0
        if len(diet_data) > 0:
            avg_calories = sum(item.get('calories', 0) for item in diet_data) // len(diet_data)
            protein_values = [item.get('protein', 0) for item in diet_data if item.get('protein') is not None]
            if protein_values:
                avg_protein = sum(protein_values) / len(protein_values)
                avg_protein = round(avg_protein, 1)
        
        # 计算训练频率
        training_sessions = len(training_data)
        
        # 计算活跃天数（任意一种活动记录的天数）
        all_dates = set()
        for data_list in [running_data, steps_data, training_data]:
            all_dates.update(item.get('date') for item in data_list)
        active_days = len(all_dates)
        
        # 获取主要情绪状态
        predominant_mood = "未记录"
        if len(mood_data) > 0:
            mood_counts = {}
            for item in mood_data:
                mood = item.get('mood')
                if mood:
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1
            if mood_counts:
                predominant_mood = max(mood_counts.items(), key=lambda x: x[1])[0]
        
        # 获取目标值
        try:
            health_goal = await sync_to_async(lambda: HealthGoal.objects.get(user=request.user))()
            weight_target = health_goal.target_weight
            steps_target = health_goal.daily_steps_goal
            sleep_target_hours = health_goal.daily_sleep_hours_goal
            sleep_target_minutes = health_goal.daily_sleep_minutes_goal
            running_distance_goal = health_goal.weekly_running_distance_goal
            training_sessions_goal = health_goal.weekly_training_sessions_goal
            calories_goal = health_goal.daily_calories_goal
            
            # 计算与目标的差距
            weight_diff = ""
            if latest_weight and weight_target:
                diff = latest_weight - weight_target
                weight_diff = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"
        except:
            weight_target = "未设置"
            steps_target = "未设置"
            sleep_target_hours = "未设置"
            sleep_target_minutes = "未设置"
            running_distance_goal = "未设置"
            training_sessions_goal = "未设置"
            calories_goal = "未设置"
            weight_diff = "未知"
        
        # 计算睡眠目标的完整表示
        sleep_target = "未设置"
        if sleep_target_hours != "未设置":
            sleep_target = f"{sleep_target_hours}h {sleep_target_minutes}min"
        
        # 确定用户的成就
        achievements = []
        if avg_steps > 0 and steps_target != "未设置" and avg_steps >= steps_target:
            achievements.append(f"平均步数达到目标 ({avg_steps} 步/天)")
        if running_sessions > 0:
            achievements.append(f"保持跑步习惯 (每周 {running_sessions} 次)")
        if avg_sleep_hours > 7:
            achievements.append(f"良好的睡眠时间 (平均 {avg_sleep_hours} 小时/晚)")
        if latest_weight and weight_target and abs(latest_weight - weight_target) < 3:
            achievements.append(f"体重接近目标值 ({latest_weight} kg)")
        if avg_calories > 0 and calories_goal != "未设置":
            achievements.append(f"保持饮食记录习惯")
        if active_days >= 5:
            achievements.append(f"每周保持 {active_days} 天活跃")
        
        # 如果没有足够的成就，添加一些默认的
        if len(achievements) < 2:
            if len(steps_data) > 0:
                achievements.append("持续记录步数数据")
            if len(sleep_data) > 0:
                achievements.append("持续记录睡眠数据")
            if len(running_data) > 0:
                achievements.append("坚持进行跑步锻炼")
            if len(training_data) > 0:
                achievements.append("坚持进行力量训练")
        
        # 选择前3个成就
        achievements = achievements[:3]
        achievements_text = ", ".join(achievements)
        
        # Create prompt for DeepSeek API with actual user data
        prompt = f"""
        Generate a personalized fitness recommendation based on the following user data in 200-300 English words. Structure it in 2-3 cohesive paragraphs without any markdown formatting.
        
        Begin by positively acknowledging their recent achievements in {achievements_text}. Then provide specific suggestions addressing these key areas:
        
        Goal Alignment: Current goals are weight target: {weight_target} kg, daily steps goal: {steps_target} steps, sleep goal: {sleep_target}, weekly running distance goal: {running_distance_goal} km, weekly training sessions goal: {training_sessions_goal}, suggest incremental improvements based on their height: {height} cm, weight: {latest_weight} kg, and consistency.
        
        Activity Optimization: Recommend exercise types/duration considering their running sessions: {running_sessions} per week, running pace: {avg_running_pace} min/km, training sessions: {training_sessions} per week.
        
        Diet & Recovery Strategy: Address sleep patterns (current {avg_sleep_hours} hours/night), diet (current {avg_calories} calories/day, {avg_protein} g protein/day), predominant mood: {predominant_mood}, and rest days.
        
        Progress Tracking: Suggest 2-3 measurable metrics to monitor across different health aspects.
        
        Maintain an encouraging tone using phrases like "Great job with..." and "You might consider...". Include 1-2 motivational quotes from famous athletes. Conclude by emphasizing sustainable habit-building. Add brief disclaimer to consult healthcare provider before major changes.
        
        User Data:
        Demographics: Age: {user_age}, Gender: {user_gender}, Height: {height} cm, Weight: {latest_weight} kg, BMI: {bmi}
        Current Goals: Weight target: {weight_target} kg, Daily steps target: {steps_target}, Sleep target: {sleep_target}, Weekly running distance: {running_distance_goal} km, Weekly training sessions: {training_sessions_goal}, Daily calories target: {calories_goal}
        
        Weekly Average:
        Steps: {avg_steps} steps/day
        Exercise: {training_sessions} training sessions, {running_sessions} running sessions
        Running: {avg_running_distance} km, {avg_running_pace} min/km pace
        Sleep: {avg_sleep_hours} hours/night
        Diet: {avg_calories} calories/day, {avg_protein} g protein/day
        Mood: {predominant_mood}
        Weight: {latest_weight} kg, {weight_diff} kg from target
        Active Days: {active_days}/7
        
        Recent Progress: {achievements_text}
        """
        
        # 使用OpenAI客户端调用DeepSeek API
        api_key = "sk-185da6fa5b874706b5254969e3531c75"  # 替换为实际的API密钥
        
        # 初始化OpenAI客户端（使用DeepSeek的API基础URL）
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        # 构建请求参数
        messages = [
            {"role": "system", "content": "You are a health and fitness advisor with expertise in analyzing health data patterns and providing personalized recommendations."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # 发送请求到DeepSeek API
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=1.0,
                max_tokens=2000
            )
            
            # 获取回复内容
            advice = response.choices[0].message.content
            generated_time = timezone.now()
            
            # 格式化建议内容为HTML，确保不包含任何标题标签或特殊格式
            formatted_advice = ""
            paragraphs = advice.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # 移除可能的Markdown或HTML标记
                    clean_para = para.strip()
                    # 将段落包装在p标签中
                    formatted_advice += f"<p>{clean_para}</p>"
            
            # 保存建议到数据库
            await sync_to_async(save_advice_to_db)(request.user, formatted_advice)
            
            return JsonResponse({
                'advice': formatted_advice,
                'generated_time': generated_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as api_error:
            return JsonResponse({'error': f'API调用错误: {str(api_error)}'}, status=500)
                    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def save_advice_to_db(user, advice_content):
    """保存生成的建议到数据库"""
    # 内容已经在生成时格式化为HTML，无需再次处理
    HealthAdvice.objects.create(
        user=user,
        content=advice_content
    )
    # 保留最新的5条建议，删除更早的
    old_advice = HealthAdvice.objects.filter(user=user)[5:]
    if old_advice.exists():
        for advice in old_advice:
            advice.delete()

# Convert sync view to async view
def generate_advice(request):
    """Synchronous wrapper for the async generate_advice view"""
    try:
        result = asyncio.run(generate_advice_async(request))
        return result
    except Exception as e:
        return JsonResponse({'error': f'处理请求时出错: {str(e)}'}, status=500)
