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
            student = Student.objects.get(id=student_id)
            student.user.delete()  # This will also delete student because of on_delete=models.CASCADE
            return Response({"message": "Student deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Student.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    
    
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


class AdmissionScheduleView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the admission schedule(s).
        """
        schedules = AdmissionSchedule.objects.all()
        serializer = AdmissionScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, *args, **kwargs):
        """
        Edit the existing admission schedule (no ID needed).
        """
        schedule = AdmissionSchedule.objects.first()  # Assuming there's only one schedule
        if schedule:
            serializer = AdmissionScheduleSerializer(schedule, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "No schedule found."}, status=status.HTTP_404_NOT_FOUND)
