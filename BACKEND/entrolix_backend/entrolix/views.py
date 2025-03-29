from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
# from django.contrib.auth.models import User
from .serializers import UserLoginSerializer,StudentRegistrationSerializer,SubadminSerializer
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

# @api_view(['GET'])
# def test_api(request):
#     data = {"message": "Frontend is connected to Backend!"}
#     serializer = TestSerializer(data)
#     return Response(serializer.data)
