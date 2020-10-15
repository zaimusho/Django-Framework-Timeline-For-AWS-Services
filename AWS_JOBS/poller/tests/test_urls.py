from django.test import TestCase
from django.urls import reverse, resolve
from poller.views import ideal_func, request_service, instance_status

class TestUrls(TestCase):
    
    def test_home_poller_url(self):
        url_path = reverse("home-poller")  
        resolve_url = resolve(url_path)
        
        assert resolve_url.view_name == "home-poller"
        self.assertEqual(resolve_url.func, ideal_func)
        
    def test_create_details_url(self):
        url_path = reverse("create-details")  
        resolve_url = resolve(url_path)
        
        assert resolve_url.view_name == "create-details"
        self.assertEqual(resolve_url.func, request_service)
        
    def test_status_logger_url(self):
        url_path = reverse("status-logger")  
        resolve_url = resolve(url_path)
        
        assert resolve_url.view_name == "status-logger"
        self.assertEqual(resolve_url.func, instance_status)