from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from WellLog.views import AboutPageView, HomePageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('health/', include('health.urls')),
    path('community/', include('community.urls')),
    path('analysis/', include('analysis.urls', namespace='analysis')),
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
]

# Add media files URL during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
