from django.db import models

# Create your models here.

class arnDetails(models.Model):
    SERVICES = (
        ('vpn', 'vpn'),
        ('S3', 'S3')
    )
    region = models.CharField(max_length=100, null=True)
    service = models.CharField(max_length=20, null=True, choices=SERVICES)
    apis = models.CharField(max_length=100, null=True)
    arn = models.CharField(max_length=200, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    
    

    
    
    