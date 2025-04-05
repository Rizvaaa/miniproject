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
                 "id":user.student.id,
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



class StudentApplicationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    student_name = serializers.SerializerMethodField()

    course_name = serializers.CharField(required=False, allow_blank=True)
    admit_card = serializers.ImageField(required=False)
    fee_reciept = serializers.ImageField(required=False)
    sslc_certificate = serializers.ImageField(required=False)
    plus_two_certificate = serializers.ImageField(required=False)
    passport_size_photo = serializers.ImageField(required=False)
    income_certificate = serializers.ImageField(required=False)
    annual_income = serializers.IntegerField(default=0)
    migration_certificate = serializers.ImageField(required=False)
    community_certificate = serializers.ImageField(required=False)
    nativity_certificate = serializers.ImageField(required=False)
    transfer_certificate = serializers.ImageField(required=False)
    conduct_certificate = serializers.ImageField(required=False)
    physical_certificate = serializers.ImageField(required=False)
    is_approved = serializers.BooleanField(default=False)

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def create(self, validated_data):
        return StudentApplication.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.student = validated_data.get('student', instance.student)
        instance.course_name = validated_data.get('course_name', instance.course_name)
        instance.admit_card = validated_data.get('admit_card', instance.admit_card)
        instance.fee_reciept = validated_data.get('fee_reciept', instance.fee_reciept)
        instance.sslc_certificate = validated_data.get('sslc_certificate', instance.sslc_certificate)
        instance.plus_two_certificate = validated_data.get('plus_two_certificate', instance.plus_two_certificate)
        instance.passport_size_photo = validated_data.get('passport_size_photo', instance.passport_size_photo)
        instance.income_certificate = validated_data.get('income_certificate', instance.income_certificate)
        instance.annual_income = validated_data.get('annual_income', instance.annual_income)
        instance.community_certificate = validated_data.get('community_certificate', instance.community_certificate)
        instance.migration_certificate = validated_data.get('community_certificate', instance.community_certificate)
        instance.nativity_certificate = validated_data.get('nativity_certificate', instance.nativity_certificate)
        instance.transfer_certificate = validated_data.get('transfer_certificate', instance.transfer_certificate)
        instance.conduct_certificate = validated_data.get('conduct_certificate', instance.conduct_certificate)
        instance.physical_certificate = validated_data.get('physical_certificate', instance.physical_certificate)
        instance.is_approved = validated_data.get('is_approved', instance.is_approved)
        instance.save()
        return instance
    


class NotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.IntegerField()  
    message = serializers.CharField(max_length=255)
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField()

    def to_representation(self, instance):
       
        return {
            'id': instance.id,
            'user': instance.user.id,  
            'message': instance.message,
            'is_read': instance.is_read,
            'created_at': instance.created_at.isoformat(),  
        }