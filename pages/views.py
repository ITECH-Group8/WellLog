from django.views.generic import TemplateView
from django.shortcuts import redirect


class HomePageView(TemplateView):
    template_name = "pages/home.html"
    
    # Remove redirection logic when logged in, allow all users to access the home page
    # def get(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect('dashboard')
    #     return super().get(request, *args, **kwargs)


class AboutPageView(TemplateView):
    template_name = "pages/about.html"
