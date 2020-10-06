
import logging
import sys
import pprint, json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import arnDetails
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
        
    }
]


def idealFunc(request):
    context = {}

    return render(request, "poller/viewer.html", context=context)


def serviceDetail(request):

    response = dict()
    
    if request.method == 'POST':
        region = request.POST['REGION']
        service = request.POST['SERVICE']
        api = request.POST['API']
        roleARN = request.POST['ROLEARN']
        
        if roleARN:
            response["region"] = region
            response["service"] = service
            response["apis"] = api
            response["roleArn"] = roleARN
            
            # info = userModel(region=region,service=service,apis=api,arn=roleARN)
            # info.save()
            # model = userModel.objects.all()
            # print(model.first)
            # print(response)
        
    else:
        print("Request not accessed !!! ")
        sys.exit(1)
        
    return response


def requestService(request):
    context = {}
    return render(request, "poller/arnDetails.html", context=context)


# Controller method for "STS rules" aws service api
   
def ingestAPICall(response):
    
    # Logging attributes status for the spinned instances using AssumeRole methodology
    
    if response["roleArn"]:
        try:
            awsObj = layerClass(REGION=response["region"])
            assumeRole = awsObj.awsSTSRole(apiCall=response["apis"], roleARN=response["roleArn"])
            credentials = awsObj.roleDataExtraction(assumeRoleCredentials=assumeRole)
            logger.debug("STS rule controller for AWS ")
            
            
        except Exception as err:
            logger.exception("Loggging STS Error: "+ str(err) + "\n")
            raise
            sys.exit(1)

        else:
            return credentials
    
    else:
        logger.exception("Role ARN missing to execute the Boto3 API call ! ")
        raise
        sys.exit(1)
  
        
def instanceController(region, externCall, credentials):
        
    try:
        awsInstance = layerClass(REGION=region)
        logger.info("Spinning the AWS Instance with STS Credentials .")
        objStatus = awsInstance.clientSpinStatusCheck(externService=externCall, tmpCredentials=credentials)
        
    except Exception as err:
        logger.exception("Loggging spinned Instance fatal error: "+ str(err) + "\n")
        raise
        sys.exit(1)
        
    else:
        return objStatus

@login_required
def instanceStatus(request):
    
    # calling the ingestAPI and then instanceController to address the status 
    # for different AWS spinned instances irrespective of their server locations
    try:
        response = serviceDetail(request)
        assumeRoleCreds = ingestAPICall(response)
        instanceData = instanceController(response["region"], response["service"], credentials=assumeRoleCreds)
        # pprint.pprint(instanceData)
        
    except Exception as err:
        logger.exception("Error while Executing the InstanceStatus method: "+ str(err) + "\n")
        sys.exit(1)
    
    else:
        context = {
            "instances": instanceData
        }
        
    return render(request, "poller/instanceStatus.html", context=context)
