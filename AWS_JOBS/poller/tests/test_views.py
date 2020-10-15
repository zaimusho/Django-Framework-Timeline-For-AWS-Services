
# taking current frame / script to inspect the workin env file
import os
# inlining the django settings modules for environ patching
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AWS_JOBS.settings")

"""
----- importing the reproduced relative path for apps imports -------
# # import sys, inspect
# # for mocking the request and user logging isntances
# # extracting the base dir of the activated environ with os.environ
# currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentDir = os.path.dirname(currentDir)
# # adding sub-directory to the python-path for relative imports
# # so that it imports modules as normal scripts
# sys.path.insert(0, parentDir)
-------------------------------------------------------------------

"""

# opposes the revoking of 3rd party django application
import django
django.setup()

import sys
import unittest
from unittest.mock import patch, Mock, MagicMock
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from poller.views import ideal_func, instance_status, service_detail, instance_controller, ingest_api_call
from mixer.backend.django import mixer
from poller.abstraction import AbstractionLayer
sys.modules["abstraction"] = Mock()
sys.modules["boto3"] = Mock()

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home-poller")
        self.detail_url = reverse("create-details")
        self.status_url = reverse("status-logger")
        self.abstraction_mock = sys.modules["abstraction"].AbstractionLayer
        self.boto3_mock = sys.modules["boto3"]
        self.mock_region = "us-east-1"
        self.mock_extern_call = "ec2"
        self.mock_credentials = [
                        "mock_security_id",
                        "mock_security_secret",
                        "mock_security_token",

        ]
        

    def test_ideal_func_request_template_check(self):
        response = self.client.get(self.home_url)

        assert response.status_code == 200
        self.assertTemplateUsed(response, 'poller/viewer.html')


    def test_ideal_func_request_method_check(self):
        request = RequestFactory().get(self.home_url)
        response = ideal_func(request)

        assert response.status_code == 200


    def test_request_service_template_check(self):
        response = self.client.get(self.detail_url)

        assert response.status_code == 200
        self.assertTemplateUsed(response, 'poller/arnDetails.html')


    def test_request_service_method_check(self):
        request = RequestFactory().get(self.detail_url)
        response = ideal_func(request)

        assert response.status_code == 200


    def test_service_details_method_post_action(self):
        request = RequestFactory().post(self.detail_url,
                                        {
                                            'REGION': 'mock-region',
                                            'SERVICE': 'mock-ec2',
                                            'API': 'mock-api',
                                            'ROLEARN': 'mockArn:12345'

                                        })
        response = service_detail(request)

        assert response['region'] == 'mock-region'
        assert response['service'] == 'mock-ec2'
        assert response['apis'] == 'mock-api'
        assert response['roleArn'] == 'mockArn:12345'


    def test_service_details_method_get_action(self):

        # with patch('sys.exit') as sys_exit:
        #     request = RequestFactory().get(self.detail_url)
        # response = serviceDetail(request=request)

        # another way-out for handling the sys.exit(1) exceptions

        request = RequestFactory().get(self.detail_url)
        with self.assertRaises(SystemExit) as sys_exit:
            service_detail(request)

        self.assertEqual(sys_exit.exception.code, 1)

    @patch("poller.abstraction.AbstractionLayer.aws_sts_role")
    @patch("poller.abstraction.AbstractionLayer.role_data_extraction")
    def test_ingest_api_call_try_catch(self, sts_role_mock, data_extraction_mock):
        mock_arn = {
            "region": self.mock_region,
            "apis": self.mock_extern_call,
            "roleArn": "mock_roleArn"

        }

        self.abstraction_mock = Mock(return_value = "mock_region")
        sts_role_mock.return_value = {"apis": "mock_ec2", 
                                    "roleArn": self.mock_extern_call, 
                                    
                                    }
        data_extraction_mock.return_value = {
                                            "key": "mock_key",
                                            "secret": "mock_secret",
                                            "token": "mock_token",
                                        }
        ingest_api_call(mock_arn)


    def test_ingest_api_call_exception_catch(self):
        mock_arn = {"roleArn": "mock_roleArn",
                    "region": self.mock_region}

        with self.assertRaises(SystemExit) as sys_exit:
            self.abstraction_mock = MagicMock(side_effect = Exception("Logging STS Error: 'apis'"))
            # print(self.abstraction_mock)
            ingest_api_call(mock_arn)

        self.assertEqual(sys_exit.exception.code, 1)


    def test_ingest_api_call_exit_method(self):
        mock_arn = {"roleArn": ""}
        with self.assertRaises(SystemExit) as sys_exit:
            ingest_api_call(mock_arn)

        self.assertEqual(sys_exit.exception.code, 1)

    @patch("poller.abstraction.AbstractionLayer.client_spin_status_check")
    def test_instance_controller_try_catch(self, status_check_mock):
        region = self.mock_region
        api = self.mock_extern_call
        credentials = {
                    "key": "mock_key",
                    "secret": "mock_secret",
                    "token": "mock_token",
                }

        self.abstraction_mock = Mock(return_value = "us-east-2")
        status_check_mock.return_value = {
                                        "service": "mock_1",
                                        "status": "stop",
                                        "instanceID": "hexadecimal_mock_id",
                                        "timestamp": "mock_timestamp",
                                        "memory": "mock_memory",

                                        }

        instance_controller(region, api, credentials)


    # need to mock the respective working func
    def test_instance_controller_exception_handling(self):
        
        with self.assertRaises(SystemExit) as sys_exit:
            self.abstraction_mock = Mock(return_value = self.mock_region)
            # print(self.abstraction_mock)  
            instance_controller(self.mock_region, "ec2", self.mock_credentials)

        self.assertEqual(sys_exit.exception.code, 1)

    
    @patch("poller.views.service_detail")
    @patch("poller.views.ingest_api_call")
    @patch("poller.views.instance_controller")
    def test_instance_status_try_catch(self, mock_service, mock_ingest_api, mock_instance_controller):
        # mocking Request Method for accessing the AWS
        request = RequestFactory().post(self.status_url,
                                        {
                                            'REGION': 'moc-region',
                                            'SERVICE': 'mock-ec2',
                                            'API': 'mock-api',
                                            'ROLEARN': 'mockArn:12345'

                                        })

        # using the User modeld for verify authenticated login check
        request.user = mixer.blend(User)
        mock_service.return_value = {
                                    "key": "mock_key",
                                    "secret": "mock_secret"
                                    
                                }

        instance_status(request)

        
    def test_instance_status_exception_handling(self):
        request = self.client.get(self.status_url, )

        # using the User modeld for verify authenticated login check
        request.user = mixer.blend(User)
        with self.assertRaises(SystemExit) as sys_exit:
            instance_status(request)
        
        self.assertEqual(sys_exit.exception.code, 1)
        assert request.status_code == 302