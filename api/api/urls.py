from django.urls import path, include
from django.contrib import admin
from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rides.urls')),
] + debug_toolbar_urls()