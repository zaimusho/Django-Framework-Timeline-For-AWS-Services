
import logging
import pprint, json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import arnDetails as userModel


# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger(__name__)
loggingFormat = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=loggingFormat)
logger.setLevel(logging.DEBUG)


def home(request):
    
    context = {
        'posts': ['0', 'new title', 'title', 'undetailed heading'
        ],
        
        'comments':['1', 'new title', 'unmentioned comment ! '
        ]
    }
    
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

def details(request):
    context = {}
    return render(request, "poller/arnDetails.html", context=context)

def instanceStatus(request):
    context = {}
    
    return render(request, "poller/instanceStatus.html", context=context)