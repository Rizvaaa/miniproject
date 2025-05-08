from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
# from django.contrib.auth.models import User
from . models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
  



class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response({
                "message": "Login successful",
                "data": serializer.validated_data
            },status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class StudentRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = StudentRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.save()  # Save returns the custom dict
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, student_id, *args, **kwargs):
        try:
            student = Student.objects.get(user__id=student_id)  # Fix: filter via user ID
            student.user.delete()  # This deletes both User and Student due to CASCADE
            return Response({"message": "Student deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Student.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
          return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class SubadminRegistrationView(APIView):
    def get(self, request):
        """List all sub‑admins"""
        subs = Subadmin.objects.select_related('user').all()
        serializer = SubadminSerializer(subs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new sub‑admin"""
        serializer = SubadminSerializer(data=request.data)
        if serializer.is_valid():
            
            serializer.save()
            return Response(
                {"message": "Sub‑admin registered successfully."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({"message": "Sub-admin deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "Sub-admin not found."}, status=status.HTTP_404_NOT_FOUND) 
    
    
class StudentemailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        applications = StudentApplication.objects.filter(is_approved=True)

        data = [
            {
                "name": f"{app.student.user.first_name} {app.student.user.last_name}",
                "id":app.student.user.id,
                "email": app.student.user.email,
                "course_name": app.course_name
            }
            for app in applications
        ]

        return Response(data, status=status.HTTP_200_OK)


class CertificateUploadAPIView(APIView):

    def get(self, request, *args, **kwargs):
        applications = StudentApplication.objects.filter(is_approved=False)
        serializer = StudentApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student')  # Student ID from the request

        if not student_id:
            return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if an application already exists for the student
        if StudentApplication.objects.filter(student_id=student_id).exists():
            return Response({"error": "An application already exists for this student."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, application_id, *args, **kwargs):
        application = get_object_or_404(StudentApplication, id=application_id)
        application.is_approved = True
        application.save()

        Notification.objects.create(
            user=application.student.user,
            message="✅ Your application has been approved! Welcome to Calicut University Institute of Engineering and Technology 🎉"
        )

        serializer = StudentApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, application_id, *args, **kwargs):
        application = get_object_or_404(StudentApplication, id=application_id)
        
        # Save user before deleting application
        user = application.student.user

        application.delete()

        Notification.objects.create(
            user=user,
            message="❌ Your application has been rejected. Please contact the administration for further details."
        )

        return Response({"message": "Application deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class NotificationAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is not None:
            user = get_object_or_404(User, id=user_id)
            notifications = Notification.objects.filter(user=user)
        else:
            notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class DashboardStatsView(APIView):
    def get(self, request):
        total_users = User.objects.count()
        total_subadmins = Subadmin.objects.count()
        total_applications = StudentApplication.objects.count()

        # Only approved applications
        approved_applications = StudentApplication.objects.filter(is_approved=True)
        total_students = approved_applications.count()

        # Department-wise counts (only approved applications)
        cs_students = approved_applications.filter(course_name__iexact="CS").count()
        mech_students = approved_applications.filter(course_name__iexact="ME").count()
        elec_students = approved_applications.filter(course_name__iexact="EEE").count()
        ce_students = approved_applications.filter(course_name__iexact="EP").count()
        print_students = approved_applications.filter(course_name__iexact="PT").count()
        electronics_students = approved_applications.filter(course_name__iexact="EC").count()

        # Type-wise counts (MERIT vs NRI)
        merit_students = approved_applications.filter(type__iexact='Merit').count()
        nri_students = approved_applications.filter(type__iexact='NRI').count()

        # Pending = not approved
        pending_students = StudentApplication.objects.filter(is_approved=False).count()

        return Response({
            "total_users": total_users,
            "total_students": total_students,
            "total_subadmins": total_subadmins,
            "total_applications": total_applications,
            "pending_students": pending_students,
            "department_counts": {
                "CS": cs_students,
                "ME": mech_students,
                "EEE": elec_students,
                "EP": ce_students,
                "PT": print_students,
                "EC": electronics_students
            },
            "type_counts": {
                "merit": merit_students,
                "nri": nri_students
            }
        }, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AdmissionSchedule
from .serializers import AdmissionScheduleSerializer

class AdmissionScheduleView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get all admission schedules.
        """
        schedules = AdmissionSchedule.objects.all()
        serializer = AdmissionScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id, *args, **kwargs):
        """
        Edit a specific admission schedule by ID.
        """
        try:
            schedule = AdmissionSchedule.objects.get(id=id)
        except AdmissionSchedule.DoesNotExist:
            return Response({"error": "Schedule not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdmissionScheduleSerializer(schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        role = request.data.get('role')  # 'student' or 'subadmin'

        if not email or not role:
            return Response({'detail': 'Email and role are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Role verification
        if role == 'student' and not hasattr(user, 'student'):
            return Response({'detail': 'Email not associated with a student account.'}, status=status.HTTP_400_BAD_REQUEST)
        if role == 'subadmin' and not hasattr(user, 'subadmin'):
            return Response({'detail': 'Email not associated with a subadmin account.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a new random password
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.set_password(new_password)
        user.save()

        # Send the new password via email
        send_mail(
            'Your Password has been Reset',
            f'Hello, your new password is: {new_password}\nPlease login .',
            'your_email@gmail.com',
            [email],
            fail_silently=False,
        )

        return Response({'detail': 'A new password has been sent to your email.'}, status=status.HTTP_200_OK)


from django.utils.http import urlsafe_base64_decode

class ResetPasswordConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except:
            return Response({'detail': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password reset successful'})





class ChatMessageView(APIView):
    def get(self, request):
        messages = ChatMessage.objects.select_related('student__user').prefetch_related('replies').all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        student_id = request.data.get('student_id')
        text = request.data.get('text')
        student = Student.objects.get(id=student_id)
        msg = ChatMessage.objects.create(student=student, text=text)
        return Response(ChatMessageSerializer(msg).data, status=201)

class SubadminReplyView(APIView):
    def post(self, request, message_id):
        message = ChatMessage.objects.get(id=message_id)
        reply_text = request.data.get('reply_text')
        reply = SubadminReply.objects.create(message=message, reply_text=reply_text)
        return Response(SubadminReplySerializer(reply).data, status=201)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class StudentEligibilityAPIView(APIView):
    def get(self, request, *args, **kwargs):
        approved_applications = StudentApplication.objects.filter(is_approved=True, type__iexact='merit')
        data = []

        for app in approved_applications:
            data.append({
                'name': f"{app.student.user.first_name} {app.student.user.last_name}",
                'income': app.annual_income,
                'course': app.course_name,
                'category': app.type,  # Should be 'Merit'
                # 'egrantz': '✅ Yes',
                # 'pms': '✅ Yes',
                # 'mcm': '✅ Yes',
                # 'css': '✅ Yes',
            })

        return Response(data, status=status.HTTP_200_OK)
