
import logging
import pprint, json
from django.db import models

# Create your models here.

# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger(__name__)
loggingFormat = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=loggingFormat)
logger.setLevel(logging.DEBUG)


class arnDetails(models.Model):
    region = models.CharField(max_length=100, null=True)
    service = models.CharField(max_length=20, null=False)
    apis = models.CharField(max_length=100, null=True)
    arn = models.CharField(max_length=200, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    
logger.info(arnDetails)



    
    
    