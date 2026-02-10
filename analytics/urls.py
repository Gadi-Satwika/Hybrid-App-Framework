# analytics/urls.py
from django.urls import path
from .views import CSVUploadView,generate_pdf_report, delete_history


urlpatterns = [
    path('upload/', CSVUploadView.as_view(), name='csv-upload'),
    path('report/<int:report_id>/', generate_pdf_report, name='pdf-report'),
    path('delete/<int:report_id>/', delete_history, name='delete-history'),
]