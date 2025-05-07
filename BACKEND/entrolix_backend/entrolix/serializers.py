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
                 "id":user.id,
                 "studentId":user.student.id,

            }
        
        raise serializers.ValidationError("Your account is not associated with any role.")
    
class StudentRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        user = User.objects.create(
            username=email,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        user.set_password(password)
        user.save()

        student = Student.objects.create(user=user)

        return {
            "id": user.id,
            "studentId": student.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }
            
class SubadminSerializer(serializers.Serializer):
    
    id = serializers.IntegerField(source='user.id', read_only=True)
 
    username     = serializers.CharField(max_length=150)
    email        = serializers.EmailField()
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
        words = ["Eagle", "Lion", "Panther", "Shark", "Tiger", "Wolf", "Hawk"]
        special_chars = "!@#$%^&*"
        w1, w2 = random.sample(words, 2)
        num    = str(random.randint(10, 99))
        sym    = random.choice(special_chars)
        return f"{w1}{sym}{w2}{num}"

    def create(self, validated_data):
     
        username    = validated_data.pop('username')
        email       = validated_data.pop('email')
        phone       = validated_data.pop('phone_number')
        password    = self.generate_random_password()

       
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()

        subadmin = Subadmin.objects.create(user=user, phone_number=phone)

        send_mail(
            subject="Your Sub‑admin Account Credentials",
            message=(
                f"Hello {username},\n\n"
                f"Your sub‑admin account has been created.\n"
                f"Username: {username}\n"
                f"Password: {password}\n\n"
                "Please log in and change your password."
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return subadmin

    def to_representation(self, instance):
        # instance is a Subadmin object
        return {
            "id":           instance.user.id,
            "username":     instance.user.username,
            "email":        instance.user.email,
            "phone_number": instance.phone_number,
        }
    
 


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
    community_certificate = serializers.ImageField(required=False)
    nativity_certificate = serializers.ImageField(required=False)
    transfer_certificate = serializers.ImageField(required=False)
    conduct_certificate = serializers.ImageField(required=False)
    physical_certificate = serializers.ImageField(required=False)
    type = serializers.CharField( default='MERIT')

    is_approved = serializers.BooleanField(default=False)

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name} "
    
    def get_student_email(self, obj):
        return obj.student.user.email

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
        instance.nativity_certificate = validated_data.get('nativity_certificate', instance.nativity_certificate)
        instance.transfer_certificate = validated_data.get('transfer_certificate', instance.transfer_certificate)
        instance.conduct_certificate = validated_data.get('conduct_certificate', instance.conduct_certificate)
        instance.physical_certificate = validated_data.get('physical_certificate', instance.physical_certificate)
        instance.type = validated_data.get('type', instance.type)
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
    

class AdmissionScheduleSerializer(serializers.ModelSerializer):
    department_display = serializers.SerializerMethodField()
    time_of_joining_display = serializers.SerializerMethodField()
    date_of_joining_display = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionSchedule
        fields = [
            'id',
            'department',
            'department_display',
            'date_of_joining',
            'date_of_joining_display',
            'time_of_joining',
            'time_of_joining_display'
        ]

    def get_department_display(self, obj):
        return obj.get_department_display()

    def get_time_of_joining_display(self, obj):
        return obj.time_of_joining.strftime("%I:%M %p") if obj.time_of_joining else None

    def get_date_of_joining_display(self, obj):
        return obj.date_of_joining.strftime("%d %B %Y") if obj.date_of_joining else None


class SubadminReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubadminReply
        fields = ['id', 'message', 'reply_text', 'replied_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    replies = SubadminReplySerializer(many=True, read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'student', 'student_name', 'text', 'created_at', 'replies']

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


# serializers.py
class StudentEligibilitySerializer(serializers.Serializer):
    student_name = serializers.SerializerMethodField()
    course_name = serializers.CharField()
    type = serializers.CharField()
    annual_income = serializers.IntegerField()

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"
