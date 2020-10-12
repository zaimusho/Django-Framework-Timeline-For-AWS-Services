
import sys
import unittest
from unittest.mock import patch, Mock, MagicMock
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from poller.views import idealFunc, instanceStatus, serviceDetail, instanceController, ingestAPICall
from mixer.backend.django import mixer

sys.modules["abstraction"] = Mock()
sys.modules["boto3"] = Mock()

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse("home-poller")
        self.detail_url = reverse("create-details")
        self.status_url = reverse("status-logger")
        self.abstraction_mock = sys.modules["abstraction"]
        self.clientSpin_mock = sys.modules["abstraction"].clientSpinStatusCheck
        self.clientSpin_mock.return_value = "mocking the individual spin status"
        self.boto3_mock = sys.modules["boto3"]
        self.mock_region = "mock_region"
        self.mock_extern_call = "mock_extern_api"
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

                                        })
        response = serviceDetail(request)

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
            serviceDetail(request)

        self.assertEqual(sys_exit.exception.code, 1)


    def test_ingest_api_call_exception_catch(self):
        mock_arn = {"roleArn": "mock_roleArn",
                    "region": self.mock_region}

        with self.assertRaises(SystemExit) as sys_exit:
            self.abstraction_mock = MagicMock(side_effect = Exception("Error"))
            # self.abstraction_mock.aws
            ingestAPICall(mock_arn)

        self.assertEqual(sys_exit.exception.code, 1)


    def test_ingest_api_call_exit_method(self):
        mock_arn = {"roleArn": ""}
        with self.assertRaises(SystemExit) as sys_exit:
            ingestAPICall(mock_arn)

        self.assertEqual(sys_exit.exception.code, 1)

    #pending needs to update the betaDev profile name
    # ----------------------- continue ---------------------------------
    def test_instance_controller_try_catch(self):
        creds = self.mock_credentials
        self.abstraction_mock = Mock(return_value = self.mock_region)
        objStatus = self.clientSpin_mock.return_value
        # print(self.abstraction_mock.clientSpinStatusCheck.return_value)
        
        self.abstraction_mock.scanRegion = Mock(return_value = self.mock_region)
        self.boto3_mock.Session = Mock()
        self.boto3_mock.Session().resource = MagicMock(return_value=self.mock_extern_call)

        # response = instanceController(self.mock_region, self.mock_extern_call, creds)
        # print(response)

    # ------------------------need to rewrite the code block--------------------
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
