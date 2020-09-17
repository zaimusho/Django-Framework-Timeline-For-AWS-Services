from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import arnDetails as userModel

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
            print(model)
        
        else:
            exit()
    
    else:
        print("Reuqest not accessed !!! ")
    
    return render(request, "poller/viewer.html", context=context)

def details(request):
    context = {}
    return render(request, "poller/arnDetails.html", context=context)