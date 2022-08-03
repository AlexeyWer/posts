from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.conf.urls import url
from django.urls import include, path


schema_view = get_schema_view(
   openapi.Info(
      title="Posts API",
      default_version='v1',
      description="Документация для приложения posts",
      contact=openapi.Contact(email="werneralexey@mail.ru"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

urlpatterns += [
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), 
       name='schema-redoc'),
]