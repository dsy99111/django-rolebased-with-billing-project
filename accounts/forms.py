from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser,Appointment
from django.forms.widgets import SelectDateWidget, TimeInput
from .models import TestReport,Billing


class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser  # Use CustomUser model
        fields = ('username', 'password1', 'password2', 'role')

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser  # Use CustomUser model
        fields = ('username', 'password')

class AppointmentForm(forms.ModelForm):
    # Add patient field with queryset for selecting patient name
    patient = forms.ModelChoiceField(queryset=CustomUser.objects.filter(role='patient'))

    # Specify widgets for appointment_date and appointment_time fields
    appointment_date = forms.DateField(widget=SelectDateWidget())
    appointment_time = forms.TimeField(widget=TimeInput(attrs={'type': 'time'}))
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']

class TestReportForm(forms.ModelForm):
    class Meta:
        model = TestReport
        fields = ['report_file']

class TestReportEditForm(forms.ModelForm):
    class Meta:
        model = TestReport
        fields = ['report_file']

class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ('patient', 'doctor', 'appointment', 'total_amount', 'payment_status', 'billing_date')
