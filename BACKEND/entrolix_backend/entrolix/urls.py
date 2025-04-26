from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("login/",LoginView.as_view(),name="login"),
    path("studentregister/",StudentRegistrationView.as_view(),name="studentregister"),
    path("subadminregister/",SubadminRegistrationView.as_view(),name="subadminregister"),
    path('upload-certificates/',CertificateUploadAPIView.as_view(), name='certificate-upload'),
    path('upload-certificates/<int:application_id>/',CertificateUploadAPIView.as_view(), name='certificate-upload'),
    path('notifications/', NotificationAPIView.as_view(), name='notifications'),
    path('notifications/<int:user_id>/', NotificationAPIView.as_view(), name='user-notification-list'),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard'),
    path("email/",StudentemailAPIView.as_view(),name="email"),
    path("admission-schedule/",AdmissionScheduleView.as_view()),
    
]

