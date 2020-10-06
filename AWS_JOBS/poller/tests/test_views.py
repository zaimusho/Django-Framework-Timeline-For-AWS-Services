
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory, Client 
from django.urls import reverse
from poller.views import idealFunc, instanceStatus, serviceDetail
from mixer.backend.django import mixer


class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home-poller")
        self.detail_url = reverse("create-details")
        self.status_url = reverse("status-logger")
                
        
    def test_ideal_func_request_template_check(self):
        response = self.client.get(self.home_url)
        
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'poller/viewer.html')
         

    def test_ideal_func_request_method_check(self):
        request = RequestFactory().get(self.home_url)
        response = idealFunc(request)
        
        assert response.status_code == 200
    
    
    def test_request_service_template_check(self):
        response = self.client.get(self.detail_url)
        
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'poller/arnDetails.html')
         

    def test_request_service_method_check(self):
        request = RequestFactory().get(self.detail_url)
        response = idealFunc(request)
        
        assert response.status_code == 200
        
    
    def test_service_details_method_post_action(self):
        request = RequestFactory().post(self.detail_url,
                                        {
                                            'REGION': 'mock-region',
                                            'SERVICE': 'mock-ec2',
                                            'API': 'mock-api',
                                            'ROLEARN': 'mockArn:12345'
                                            
                                        } )
        response = serviceDetail(request)
        
        assert response['region'] == 'mock-region'
        assert response['service'] == 'mock-ec2'
        assert response['apis'] == 'mock-api'
        assert response['roleArn'] == 'mockArn:12345'
               
        
    def test_service_details_method_get_action(self):
        request = RequestFactory().get(self.detail_url)
        print(request)
    
    # need to mock the respective working func 
    def test_instance_status_authenticated(self):
        # mocking Request Method for accessing the AWS
        # report parameters
        
        request = RequestFactory().post(self.status_url, 
                                        {
                                            'REGION': 'moc-region',
                                            'SERVICE': 'mock-ec2',
                                            'API': 'mock-api',
                                            'ROLEARN': 'mockArn:12345'
                                            
                                        })
        
        request.user = mixer.blend(User)
        
        
    #     response = instanceStatus(request)
    #     print(response)
        
        # need to write the assume role code platform
        
    
