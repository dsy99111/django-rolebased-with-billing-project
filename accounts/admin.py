from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Appointment,TestReport,Doctor_Blog,Video
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    list_filter = ('role', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'role')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
# Register Appointment model with admin
@admin.register(Doctor_Blog)
class DoctorBlogAdmin(admin.ModelAdmin):
    list_display = ('sno', 'name', 'message', 'specific', 'image', 'time', 'user_id')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('vno', 'title', 'video')
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'appointment_date', 'appointment_time', 'reason')
    list_filter = ('doctor', 'patient', 'appointment_date')
    search_fields = ('doctor__username', 'patient__username', 'appointment_date')

@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ('patient', 'report_file', 'uploaded_at')
    search_fields = ('patient__username',)


