from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('secure_notes.urls')),
    path('api/', include('secure_notes.api_urls')),
    path('api-auth/', include('rest_framework.urls')),
    
]
