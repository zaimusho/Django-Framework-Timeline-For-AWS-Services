
import logging
import pprint, json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import arnDetails as userModel
from .abstraction import abstractionLayer as layerClass

# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger(__name__)
loggingFormat = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=loggingFormat)
logger.setLevel(logging.DEBUG)

# dummy data for isntance status check functionality
data = [
    {
        "instanceId": "12",
        "type": "arm",
        "lifecycle": "ended",
        "hypervisor": "None",
        "architecture": "i386",
        "rootdDevice": "/dev/sda",
        "iam": "arn::12345:12",
        "lauchtime": "2020-8-12",
        "placement": "us-east-2",
        "state": "running",
        "tranReason": "cron jobs response"
        
    },
    {
        "instanceId": "13",
        "type": "arm",
        "lifecycle": "ended",
        "hypervisor": "None",
        "architecture": "i386",
        "rootdevice": "/dev/sda",
        "iam": "arn::12345:12",
        "lauchtime": "2020-8-12",
        "placement": "us-east-2",
        "state": "running",
        "tranReason": "cron jobs response"
        
    }
]

def home(request):

    if request.method == 'POST':
        region = request.POST['REGION']
        service = request.POST['SERVICE']
        api = request.POST['API']
        roleARN = request.POST['ROLEARN']
        
        if roleARN:
            info = userModel(region=region,service=service,apis=api,arn=roleARN)
            info.save()
            model = userModel.objects.all()
            print(model.first)
        
        else:
            exit()
    
    else:
        print("Request not accessed !!! ")
    
    return render(request, "poller/viewer.html", context=context)

def requestService(request):
    context = {}
    return render(request, "poller/arnDetails.html", context=context)

# Controller method for "STS rules" aws service api
   
def ingestAPICall(request):

# jsonFile = self.dirLocation() + "/" + path
    if request.method == 'POST':
        region = request.POST['REGION']
        service = request.POST['SERVICE']
        apis = request.POST['API']
        roleARN = request.POST['ROLEARN']
        
        if roleARN:
            try:
                awsObj = layerClass(REGION=region)
                assumeRole = awsObj.awsSTSRole(apiCall=apis, roleARN=roleARN)
                credentials = awsObj.roleDataExtraction(assumeRoleCredentials=assumeRole)
                logger.debug("STS rule controller for AWS ")
                
                
            except Exception as err:
                logger.exception("Loggging STS Error: "+ str(err) + "\n")
                raise
                exit()

            else:
                return credentials
        
        else:
            logger.exception("Role ARN missing to execute the Boto3 API call ! ")
            raise
            exit()

def instanceStatus(request):
    
    context = {
        "instances": data
    }
    
    return render(request, "poller/instanceStatus.html", context=context)
