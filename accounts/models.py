from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('receptionist', 'Receptionist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')

# Create your models here.

class Doctor_Blog(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    message = models.TextField()
    specific = models.TextField()
    image = models.ImageField(upload_to='image/')
    time = models.DateTimeField(blank=True)
    user_id = models.IntegerField(null=True, blank=True)  # Allow null and blank values

    def __str__(self):
        return self.name
class Appointment(models.Model):
    doctor = models.ForeignKey(CustomUser, related_name='doctor_appointments', on_delete=models.CASCADE)
    patient = models.ForeignKey(CustomUser, related_name='patient_appointments', on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)

    def __str__(self):
        return f'Appointment - {self.doctor.username} - {self.appointment_date}'

    # Add any additional fields or methods as needed

class TestReport(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    report_file = models.FileField(upload_to='test_reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.report_file.name
class Video(models.Model):
    vno = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/')

    class Meta:
        verbose_name = 'video'
        verbose_name_plural = 'videos'

    def __str__(self):
        return self.title
