# Create your views here.
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout,authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from .forms import AppointmentForm
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Appointment,CustomUser
from .models import TestReport,Doctor_Blog,Video,Billing
from .forms import TestReportForm, TestReportEditForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import BillingForm

from reportlab.lib.units import inch
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from io import BytesIO
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
# chatbot/views.py

import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Set your OpenAI API key here
openai.api_key = 'your-openai-api-key'
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from .tokens import email_verification_token  # Import the custom token generator
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site

User = get_user_model()
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

        billing = Billing.objects.all().order_by('-billing_date')  # Example query to get the first billing object

        selected_date = request.GET.get('date')

        selected_doctor = request.GET.get('doctor')

        if selected_date:
            appointments = appointments.filter(appointment_date=selected_date)

        if selected_doctor:
            appointments = appointments.filter(doctor__username=selected_doctor)

        # Check if billing object exists before passing it to the template

        context = {'appointments': appointments, 'doctors': doctors,'billing': billing}

        return render(request, 'accounts/receptionist.html', context)

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
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email is verified
            user.save()

            # Send confirmation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('accounts/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': email_verification_token.make_token(user),
            })
            send_mail(mail_subject, message, 'webmaster@mydomain.com', [user.email])

            return redirect('email_verification_sent')  # Redirect to a page telling the user to check their email
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

@login_required
def create_billing(request):
    if request.method == 'POST':
        # Process billing creation form data
        # Make sure only receptionists can access this view
        if request.user.role != 'receptionist':
            return redirect('dashboard')  # Redirect unauthorized users

        form = BillingForm(request.POST)
        if form.is_valid():
            billing = form.save(commit=False)
            billing.save()
            return redirect('billing_details', billing_id=billing.pk)  # Redirect to billing details page for the newly created billing record
    else:
        # Display billing creation form
        # Make sure only receptionists can access this view
        if request.user.role != 'receptionist':
            return redirect('dashboard')  # Redirect unauthorized users

        form = BillingForm()
    return render(request, 'accounts/create_billing.html', {'form': form})
@login_required
def billing_details(request, billing_id):
    # Retrieve the billing object using the billing_id
    billings = get_object_or_404(Billing, billing_id=billing_id)

    # Check if the user is a receptionist before proceeding
    if request.user.role != 'receptionist':
        return redirect('dashboard')  # Redirect unauthorized users

    return render(request, 'accounts/billing_details.html', {'billings': billings})





def generate_pdf(billing):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Get the path to the image file
    image_path = os.path.join(settings.MEDIA_ROOT, 'bill-logo-image', 'lifetree.png')

    # Draw the hospital letterhead or logo image
    p.drawImage(image_path, 100, height - 150, width=200, height=100)

    # Add billing details
    p.drawString(100, height - 180, f"Billing ID: {billing.billing_id}")
    p.drawString(100, height - 200, f"Patient: {billing.patient.username}")
    p.drawString(100, height - 220, f"Doctor: {billing.doctor.username}")
    p.drawString(100, height - 240, f"Appointment: {billing.appointment}")
    p.drawString(100, height - 260, f"Total Amount: {billing.total_amount}")
    p.drawString(100, height - 280, f"Payment Status: {billing.payment_status}")
    p.drawString(100, height - 300, f"Billing Date: {billing.billing_date}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def billing_pdf_view(request, billing_id):
    billing = get_object_or_404(Billing, billing_id=billing_id)
    pdf_buffer = generate_pdf(billing)

    # Check if the request is for preview or email
    if 'preview' in request.GET:
        return HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    else:
        # Email setup
        subject = f'Billing Details for Billing ID: {billing.billing_id}'
        recipient = billing.patient.email  # Assuming Billing has a ForeignKey to the Patient model
        from_email = settings.DEFAULT_FROM_EMAIL

        # Render an optional email template
        html_message = render_to_string('email/billing_email.html', {'billing': billing})
        plain_message = strip_tags(html_message)

        # Create email
        email = EmailMessage(subject, plain_message, from_email, [recipient])
        email.attach(f'billing_{billing.billing_id}.pdf', pdf_buffer.getvalue(), 'application/pdf')

        # Send email
        email.send()

        # Provide a response
        return HttpResponse(f'Billing details have been emailed to {recipient}.')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  # Automatically log in the user
        return redirect('accounts')  # Redirect to the accounts view
    else:
        return render(request, 'accounts/activation_invalid.html')
