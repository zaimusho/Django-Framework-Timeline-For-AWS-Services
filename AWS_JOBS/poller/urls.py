
import logging
import pprint, json
from django.urls import path
from . import views

# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger(__name__)
loggingFormat = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=loggingFormat)
logger.setLevel(logging.DEBUG)


urlpatterns = [
    path('', views.idealFunc, name='home-poller'),
    path('createDetails/', views.requestService, name='create-details'),
    path('instanceStatus/', views.instanceStatus, name='status-logger')
    
]

logger.debug(urlpatterns)