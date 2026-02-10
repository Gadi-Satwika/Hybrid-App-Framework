from django.db import models

class EquipmentDataset(models.Model):
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    # We will store the summary statistics as JSON
    summary_data = models.JSONField() 

    def __str__(self):
        return self.file_name