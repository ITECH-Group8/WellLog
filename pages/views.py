from django.views.generic import TemplateView  # ✅ 确保导入 TemplateView

class HomePageView(TemplateView):
    template_name = "pages/homepage.html"

class AboutPageView(TemplateView):
    template_name = "pages/about.html"

class DashboardPageView(TemplateView):  # ✅ 改成基于类的视图
    template_name = "pages/dashboard.html"
class CommunityPageView(TemplateView):
    template_name = "pages/community.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = [
            {"content": "Just finished a 5km run today! Feeling great 💪", "likes": 50, "comments": 12, "attachment": "📸"},
            {"content": "Tried a low-carb diet for a week, and I feel much more energized! 😋", "likes": 94, "comments": 8, "attachment": "📸"},
            {"content": "Only got 5 hours of sleep last night... Feeling exhausted today. 🥱 Sleep is so important!", "likes": 66, "comments": 123, "attachment": "📊"},
        ]
        return context


class AIAdvicePageView(TemplateView):
    template_name = "pages/ai_advice.html"
