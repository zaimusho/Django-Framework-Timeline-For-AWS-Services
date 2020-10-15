
import logging
import pprint, json
from django.urls import path
from . import views

# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger(__name__)
logging_format = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=logging_format)
logger.setLevel(logging.DEBUG)


urlpatterns = [
    path('', views.ideal_func, name='home-poller'),
    path('createDetails/', views.request_service, name='create-details'),
    path('instanceStatus/', views.instance_status, name='status-logger')
    
]

logger.debug(urlpatterns)