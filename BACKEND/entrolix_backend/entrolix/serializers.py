from rest_framework import serializers
from django.contrib.auth.models import User
from .models import*
import random
# import random.
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate

class UserLoginSerializer(serializers.Serializer):
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        input_identifier = data.get("username")
        password = data.get("password")

       # if the input contains '@', treat as email
        if "@" in input_identifier:
            user = User.objects.filter(email=input_identifier).first()
        else:
            user = User.objects.filter(username=input_identifier).first()
        if not user:
            raise serializers.ValidationError("User doesn't exist.")
        
        if user.is_superuser:
            if not user.check_password(password):
                raise serializers.ValidationError("invalid credential for admin.")
            return{
                "username":user.username,
                "role":"admin",
                "message": "Admin login successful",
            }
        
        user=authenticate(username=user.username,password=password)
        if not user:
            raise serializers.ValidationError("invalid username or password.")
        
        if hasattr(user,'subadmin'):
            return{
                "username":user.username,
                "role":"subadmin",
                "message": "subadmin login successful",
            }
        
        if hasattr(user,'student'):
            return{
                "email":user.email,
                "role":"student",
                "message": "student login successful",
            }
        
        raise serializers.ValidationError("Your account is not associated with any role.")
    
class StudentRegistrationSerializer(serializers.Serializer):
        first_name=serializers.CharField(max_length=150)
        last_name=serializers.CharField(max_length=150)
        email=serializers.EmailField()
        password=serializers.CharField(write_only=True,min_length=8)


        def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("An account with this email already exist.")
            return value
        
        def create(self, validated_data):

            first_name=validated_data.pop("first_name")
            last_name=validated_data.pop("last_name")
            email=validated_data.pop("email")
            password=validated_data.pop("password")

            user= User.objects.create(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            user.set_password(password)
            user.save()

            Student.objects.create(
                user=user
            )
            return user
        
class SubadminSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=150)
    email = serializers. EmailField()
    phone_number = serializers.CharField(max_length=15)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
             raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def generate_random_password(self, length=10):
        words = ["Eagle", "Lion", "Panther", "Shark", "Tiger", "wolf", "Hawk"]
        special_chars = "1@#$%^&*"
        word1 = random.choice(words)
        word2 = random.choice(words)
        number = str(random.randint(10, 99))
        symbol = random.choice(special_chars)
        return f"{word1}{symbol}{word2}{number}"

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]
        phone_number = validated_data["phone_number"]
        random_password = self.generate_random_password()
        user = User.objects.create(username = username, email=email)
        user.set_password(random_password)
        user.save()

        subadmin = Subadmin.objects.create(user=user, phone_number=phone_number)

        send_mail(
            subject="Your subadmin accnt credentials",
            message=f"Dear {username},\n\nYour accnt has been successfullycreated!\n\nUsername:{username}\nPassword: {random_password}\n\nPlease change your password after logging in.\n",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return subadmin
