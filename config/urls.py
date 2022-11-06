from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class AuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "role": user.groups.all().first().name,
                "name": user.first_name + " " + user.last_name,
            }
        )


urlpatterns = [
    path("v1/obtain-token/", AuthToken.as_view(), name="obtain-token"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("", include("students.urls")),
    path("", include("teacher.urls")),
    path("", include("staff.urls")),
    path("", include("apps.attendances.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
