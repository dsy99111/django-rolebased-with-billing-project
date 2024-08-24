from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from . import views
from .views import register, activate
from django.views.generic import TemplateView  # Import TemplateView

urlpatterns = [

    path('',views.accounts,name="accounts"),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/',views.logout_page,name="logout_page"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_appointment/', views.create_appointment, name='create_appointment'),
    path('upload-test-report/', views.upload_test_report, name='upload_test_report'),
    path('edit-test-report/<int:report_id>/', views.edit_test_report, name='edit_test_report'),
    path('view_reports/', views.view_reports, name='view_reports'),
    path('delete/<int:report_id>/', views.delete_report, name='delete_report'),
    path('create-billing/', views.create_billing, name='create_billing'),
    path('billing/<int:billing_id>/', views.billing_details, name='billing_details'),
    path('billing/pdf/<int:billing_id>/', views.billing_pdf_view, name='billing_pdf'),
path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('email_verification_sent/', TemplateView.as_view(template_name="accounts/email_verification_sent.html"), name='email_verification_sent'),

]
urlpatterns  += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
