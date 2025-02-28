from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from pages import views
from pages.views import HomePageView, AboutPageView, DashboardPageView, CommunityPageView,AIAdvicePageView
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("pages.urls")),
    path('', HomePageView.as_view(), name='home'),  
    path('about/', AboutPageView.as_view(), name='about'),
    path('dashboard/', DashboardPageView.as_view(), name='dashboard'),
    path('community/', CommunityPageView.as_view(), name='community'),
    path('ai-advice/', AIAdvicePageView.as_view(), name='ai_advice'),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
