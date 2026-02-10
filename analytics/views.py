import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import EquipmentDataset

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework import status

from django.http import HttpResponse
from reportlab.pdfgen import canvas

from .serializers import FileUploadSerializer

class CSVUploadView(APIView):
    # This allows the view to accept file uploads
    parser_classes = [MultiPartParser]

    serializer_class = FileUploadSerializer

    def get(self, request):
        # Get last 5 records, ordered by newest first
        history = EquipmentDataset.objects.all().order_by('-upload_date')[:5]
        
        # Format the data into a list
        history_list = []
        for item in history:
            history_list.append({
                "id": item.id,
                "file_name": item.file_name,
                "date": item.upload_date.strftime("%Y-%m-%d %H:%M"),
                "summary": item.summary_data
            })
            
        return Response(history_list)

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)
        
        if not file_obj.name.endswith('.csv'):
            return Response({"error": "Invalid format. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_csv(file_obj)
            
            # --- NEW: REAL-WORLD ANOMALY DETECTION ---
            alerts = []
            # Check for high temperature (Potential Overheating)
            overheating = df[df['Temperature'] > 90]
            if not overheating.empty:
                alerts.append(f"CRITICAL: {len(overheating)} units showing overheating (>90°C)")

            # Check for low pressure (Potential Leakage)
            low_pressure = df[df['Pressure'] < 1.5]
            if not low_pressure.empty:
                alerts.append(f"WARNING: {len(low_pressure)} units showing low pressure (<1.5 bar)")

            # Calculate a Health Score (starts at 100, drops for every alert found)
            health_score = max(0, 100 - (len(overheating) * 10) - (len(low_pressure) * 5))
            # ------------------------------------------

            summary = {
                "total_count": len(df),
                "avg_flowrate": float(df['Flowrate'].mean()),
                "avg_pressure": float(df['Pressure'].mean()),
                "avg_temp": float(df['Temperature'].mean()),
                "type_distribution": df['Type'].value_counts().to_dict(),
                # Add these new keys to the response
                "health_score": health_score,
                "alerts": alerts if alerts else ["All systems operational"]
            }

            EquipmentDataset.objects.create(
                file_name=file_obj.name,
                summary_data=summary
            )

            return Response(summary, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


def generate_pdf_report(request, report_id):
    try:
        dataset = EquipmentDataset.objects.get(id=report_id)
        summary = dataset.summary_data
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Report_{report_id}.pdf"'
        
        p = canvas.Canvas(response)
        
        # Header
        p.setFont("Helvetica-Bold", 18)
        p.drawString(100, 800, "Chemical Equipment Analytics Report")
        p.line(100, 795, 500, 795)
        
        # File Info
        p.setFont("Helvetica", 12)
        p.drawString(100, 770, f"Source File: {dataset.file_name}")
        p.drawString(100, 755, f"Date Generated: {dataset.upload_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Summary Statistics Section
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 720, "Summary Statistics")
        
        p.setFont("Helvetica", 12)
        p.drawString(120, 700, f"• Total Equipment Count: {summary['total_count']}")
        p.drawString(120, 680, f"• Average Flowrate: {summary['avg_flowrate']:.2f}")
        p.drawString(120, 660, f"• Average Pressure: {summary['avg_pressure']:.2f}")
        p.drawString(120, 640, f"• Average Temperature: {summary['avg_temp']:.2f} C")
        
        # Distribution Section
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 600, "Equipment Type Distribution")
        
        y_position = 580
        p.setFont("Helvetica", 12)
        for eq_type, count in summary['type_distribution'].items():
            p.drawString(120, y_position, f"• {eq_type}: {count}")
            y_position -= 20

        # Add at the bottom of the PDF generation
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 450, "Engineering Conclusion:")
        p.setFont("Helvetica", 12)
        if summary['health_score'] < 90:
            conclusion = "Maintenance Required: Multiple equipment units are operating outside nominal bounds."
        else:
            conclusion = "Normal Operation: All parameters are consistent with plant safety standards."
        p.drawString(100, 430, conclusion)
            
        p.showPage()
        p.save()
        return response
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=404)
        

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_history(request, report_id):
    try:
        record = EquipmentDataset.objects.get(id=report_id)
        record.delete()
        return Response({"message": "Record deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except EquipmentDataset.DoesNotExist:
        return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)