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
        serializer = StudentRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"student registered successfully."},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SubadminRegistrationview(APIView):
    def post(self, request):
        serializer = SubadminSerializer(data=request.data)
        if serializer.is_valid():
            subadmin = serializer.save()
            return Response({"message": "subadmin registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CertificateUploadAPIView(APIView):

    def get(self, request, *args, **kwargs):
        applications = StudentApplication.objects.all()
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
            message=f"Your application (ID: {application.id}) has been approved!"
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