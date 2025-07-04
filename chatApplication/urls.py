"""
URL configuration for chatApplication project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import path,include
from django.contrib import admin
from drf_yasg import openapi
from chat.views import *


schema_view = get_schema_view(
   openapi.Info(
      title="Chat App API",
      default_version='v1',
      description="API documentation for Chat Application",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="support@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


#Routes for App
router = DefaultRouter()
router.register(r'hello', HelloViewSet, basename='hello')
router.register(r'ideas', IdeaViewSet, basename='ideas')

#Events apis
router.register(r'events',EventViewSet,basename='events')
router.register(r'organizers', OrganizerViewSet,basename='organizers')
router.register(r'events-price', EventPriceViewSet,basename='event-prices')
router.register(r'tickets', TicketViewSet,basename='tickets')



#swagger and apis homes
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),

    #For video call
    path('video/', index, name='index'),
     
    #Login apis and register apis
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),

    # Swagger/OpenAPI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),

]
