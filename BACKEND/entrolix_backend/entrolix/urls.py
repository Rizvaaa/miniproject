from django.urls import path
from .views import LoginView
from .views import StudentRegistrationView
from .views import SubadminRegistrationview
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("login/",LoginView.as_view(),name="login"),
    path("studentregister/",StudentRegistrationView.as_view(),name="studentregister"),
    path("subadminregister/",SubadminRegistrationview.as_view(),name="subadminregister"),
    
]


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)