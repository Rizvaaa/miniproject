from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
# from django.contrib.auth.models import User
from . models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
# from .serializers import TestSerializer


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
    def post(self, request):
        """Register a new student"""
        serializer = StudentRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Student registered successfully."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

class CertificateUploadAPIView(APIView):

    def get(self, request, *args, **kwargs):
        applications = StudentApplication.objects.filter(is_approved=False)
        serializer = StudentApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
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
            message=f"Your application has been approved! You are Successfully Enrolled as a Student in Calicut University Institute of Engineering and Technology"
        )

        serializer = StudentApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, application_id, *args, **kwargs):
        application = get_object_or_404(StudentApplication, id=application_id)
        application.delete()
        return Response({"message": "Application deleted successfully"}, status=status.HTTP_204_NO_CONTENT)# class StudentApplicationListView(APIView):


class NotificationAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        
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
        cs_students = approved_applications.filter(course_name__iexact="computer sciences").count()
        mech_students = approved_applications.filter(course_name__iexact="mechanical").count()
        elec_students = approved_applications.filter(course_name__iexact="electrical").count()
        ce_students = approved_applications.filter(course_name__iexact="computer and electronics").count()
        print_students = approved_applications.filter(course_name__iexact="printing").count()
        electronics_students = approved_applications.filter(course_name__iexact="electronics").count()

        # Type-wise counts (MERIT vs NRI)
        merit_students = approved_applications.filter(type__iexact='MERIT').count()
        nri_students = approved_applications.filter(type__iexact='NRI').count()

        return Response({
            "total_users": total_users,
            "total_students": total_students,
            "total_subadmins": total_subadmins,
            "total_applications": total_applications,
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