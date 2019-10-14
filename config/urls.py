from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from users.views import LogIn, LogOut, Settings, SignUp


urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("", include("questions.urls")),
    path("api/v1/", include("api.urls")),
    path("login", LogIn.as_view(), name="login"),
    path("logout", LogOut.as_view(), name="logout"),
    path("settings", Settings.as_view(), name="settings"),
    path("signup", SignUp.as_view(), name="signup"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
