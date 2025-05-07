from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("login/",LoginView.as_view(),name="login"),
    path("studentregister/",StudentRegistrationView.as_view(),name="studentregister"),
    path("studentregister/<int:student_id>/", StudentRegistrationView.as_view(), name="studentregister"),
    path("subadminregister/",SubadminRegistrationView.as_view(),name="subadminregister"),
    path('subadminregister/<int:pk>/', SubadminRegistrationView.as_view(), name='subadmin-delete'),
    path('upload-certificates/',CertificateUploadAPIView.as_view(), name='certificate-upload'),
    path('upload-certificates/<int:application_id>/',CertificateUploadAPIView.as_view(), name='certificate-upload'),
    path('notifications/', NotificationAPIView.as_view(), name='notifications'),
    path('notifications/<int:user_id>/', NotificationAPIView.as_view(), name='user-notification-list'),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard'),
    path("email/",StudentemailAPIView.as_view(),name="email"),
    path("admission-schedule/",AdmissionScheduleView.as_view()),
    path("admission-schedule/<int:id>/", AdmissionScheduleView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),

    path("chat/messages/", ChatMessageView.as_view()),
    path("chat/messages/<int:message_id>/reply/", SubadminReplyView.as_view()),

    path("student-eligibility/", StudentEligibilityAPIView.as_view(), name="student-eligibility"),



]