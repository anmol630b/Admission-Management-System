from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Univio Admin"
admin.site.site_title = "Univio Admin Portal"
admin.site.index_title = "Welcome to Univio Researcher Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("home.urls")),
]

# DEVELOPMENT ME STATIC + MEDIA FILES SERVE KARNE KE LIYE
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # <-- yeh add karo
handler404 = 'home.views.custom_404'
