# Create your views here.
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from .forms import AppointmentForm
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Appointment,CustomUser
from .models import TestReport,Doctor_Blog,Video
from .forms import TestReportForm, TestReportEditForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def accounts(request):
    alldoctor = Doctor_Blog.objects.all()[::-1]
    video = Video.objects.all()

    context = {'alldoctor': alldoctor, 'video': video}
    # print(allpost)
    return render(request, 'accounts/index.html', context)


@login_required
def dashboard(request):
    if request.user.role == 'doctor':
        # Retrieve appointments for the logged-in doctor
        appointments = Appointment.objects.filter(doctor=request.user).order_by('-appointment_date')

        # Handle date filtering if request contains date parameter
        selected_date = request.GET.get('date')
        if selected_date:
            appointments = appointments.filter(appointment_date=selected_date)

        # Retrieve test reports for the logged-in doctor's patients
        patients = appointments.values_list('patient', flat=True).distinct()
        test_reports = TestReport.objects.filter(patient__in=patients).order_by('-uploaded_at')

        return render(request, 'accounts/doctor.html', {'appointments': appointments, 'test_reports': test_reports})

    elif request.user.role == 'receptionist':
        appointments = Appointment.objects.all().order_by('-appointment_date')
        doctors = CustomUser.objects.filter(role='doctor')

        selected_date = request.GET.get('date')
        selected_doctor = request.GET.get('doctor')

        if selected_date:
            appointments = appointments.filter(appointment_date=selected_date)

        if selected_doctor:
            appointments = appointments.filter(doctor__username=selected_doctor)

        return render(request, 'accounts/receptionist.html', {'appointments': appointments, 'doctors': doctors})

    else:
        # Default dashboard for patients
        # Retrieve appointments for the logged-in patient
        appointments = Appointment.objects.filter(patient=request.user)[::-1]
        test_reports = TestReport.objects.filter(patient=request.user)[::-1]

        return render(request, 'accounts/patient.html', {'appointments':appointments, 'test_reports': test_reports})
        #return render(request, 'accounts/patient.html', {'appointments': appointments})
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_page(request):
    logout(request)
    messages.success(request,"Account log out")
    return redirect("/")

@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user  # Assign the logged-in patient as the appointment's patient
            appointment.save()
            messages.success(request, {'Thanks to take for appointment '})
            return redirect('dashboard')  # Redirect to the dashboard or another page
    else:
        form = AppointmentForm()
    return render(request, 'appointment/create_appointment.html', {'form': form})

@login_required
def upload_test_report(request):
    if request.method == 'POST':
        form = TestReportForm(request.POST, request.FILES)
        if form.is_valid():
            test_report = form.save(commit=False)
            test_report.patient = request.user
            test_report.save()
            return redirect('dashboard')
    else:
        form = TestReportForm()
    return render(request, 'accounts/upload_test_report.html', {'form': form})

@login_required
def edit_test_report(request, report_id):
    test_report = get_object_or_404(TestReport, id=report_id)
    if request.method == 'POST':
        form = TestReportEditForm(request.POST, request.FILES, instance=test_report)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TestReportEditForm(instance=test_report)
    return render(request, 'accounts/edit_test_report.html', {'form': form})

def view_reports(request):
    reports = TestReport.objects.filter(patient=request.user.patient)
    return render(request, 'accounts/view_reports.html', {'reports': reports})

def delete_report(request, report_id):
    report = get_object_or_404(TestReport, id=report_id)
    if request.method == 'POST':
        report.delete()
        return redirect('view_reports')
    return render(request, 'accounts/delete_report.html', {'report': report})