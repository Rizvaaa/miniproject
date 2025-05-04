from django.contrib import admin
from .models import*

# admin.site.register(Student)
admin.site.register(Subadmin)
# admin.site.register(Notification)
admin.site.register(StudentApplication)
admin.site.register(AdmissionSchedule)
admin.site.register(ChatNotification)
admin.site.register(Message)



class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'message', 'is_read', 'created_at')

admin.site.register(Notification, NotificationAdmin)



class StudentAdmin(admin.ModelAdmin):
    list_display = ('id','user')

admin.site.register(Student, StudentAdmin)



