
import logging
import sys, os, inspect
# for mocking the request and user logging isntances
# extracting the base dir of the activated environ with os.environ
currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentDir = os.path.dirname(currentDir)
# adding sub-directory to the python-path for relative imports
# so that it imports modules as normal scripts
sys.path.insert(0, parentDir)
import pprint, json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from poller.models import arnDetails
from poller.abstraction import AbstractionLayer as LayerClass

# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger(__name__)
logging_format = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=logging_format)
logger.setLevel(logging.DEBUG)

# dummy data for instance status check functionality
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


def ideal_func(request):
    context = {}

    return render(request, "poller/viewer.html", context=context)


def service_detail(request):

    response = dict()
    
    if request.method == 'POST':
        region = request.POST['REGION']
        service = request.POST['SERVICE']
        api = request.POST['API']
        role_arn = request.POST['ROLEARN']
        
        if role_arn:
            response["region"] = region
            response["service"] = service
            response["apis"] = api
            response["roleArn"] = role_arn
            
            # info = userModel(region=region,service=service,apis=api,arn=roleARN)
            # info.save()
            # model = userModel.objects.all()
            # print(model.first)
            # print(response)
        
    else:
        logger.warning("Request not accessed !!! ")
        sys.exit(1)
        
    return response


def request_service(request):
    context = {}
    return render(request, "poller/arnDetails.html", context=context)


# Controller method for "STS rules" aws service api   
def ingest_api_call(response):
    # Logging attributes status for the spinned instances using AssumeRole methodology
    
    if response["roleArn"]:
        try:
            aws_obj = LayerClass(region=response["region"])
            assume_role = aws_obj.aws_sts_role(api_call=response["apis"], role_arn=response["roleArn"])
            credentials = aws_obj.role_data_extraction(assume_role_credentials=assume_role)
            logger.debug("STS rule controller for AWS ")
            
        except Exception as err:
            logger.exception("Logging STS Error: "+ str(err) + "\n")
            sys.exit(1)

        else:
            return credentials
    
    else:
        logger.exception("Role ARN missing to execute the Boto3 API call ! ")
        sys.exit(1)
  
        
def instance_controller(region, extern_call, credentials):
        
    try:
        aws_instance = LayerClass(region=region)
        logger.info("Spinning the AWS Instance with STS Credentials .")
        obj_status = aws_instance.client_spin_status_check(extern_service=extern_call, temp_credentials=credentials)
        
    except Exception as err:
        logger.exception("Loggging spinned Instance fatal error: "+ str(err) + "\n")
        sys.exit(1)
        
    else:
        return obj_status

@login_required
def instance_status(request):
    
    # calling the ingestAPI and then instanceController to address the status 
    # for different AWS spinned instances irrespective of their server locations
    try:
        response = service_detail(request)
        assume_role_creds = ingest_api_call(response)
        instance_data = instance_controller(response["region"], response["service"], credentials=assume_role_creds)
        # pprint.pprint(instanceController)
        
    except Exception as err:
        logger.exception("Error while Executing the InstanceStatus method: "+ str(err) + "\n")
        sys.exit(1)
    
    else:
        context = {
            "instances": instance_data
        }
        
    return render(request, "poller/instanceStatus.html", context=context)
