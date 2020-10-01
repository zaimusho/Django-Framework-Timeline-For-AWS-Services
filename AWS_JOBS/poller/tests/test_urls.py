from django.test import TestCase
from django.urls import reverse, resolve
from poller.views import idealFunc, requestService, instanceStatus

class TestUrls(TestCase):
    
    def test_home_poller_url(self):
        urlPath = reverse("home-poller")  
        resolveUrl = resolve(urlPath)
        
        assert resolveUrl.view_name == "home-poller"
        self.assertEqual(resolveUrl.func, idealFunc)
        
    def test_create_details_url(self):
        urlPath = reverse("create-details")  
        resolveUrl = resolve(urlPath)
        
        assert resolveUrl.view_name == "create-details"
        self.assertEqual(resolveUrl.func, requestService)
        
    def test_status_logger_url(self):
        urlPath = reverse("status-logger")  
        resolveUrl = resolve(urlPath)
        
        assert resolveUrl.view_name == "status-logger"
        self.assertEqual(resolveUrl.func, instanceStatus)