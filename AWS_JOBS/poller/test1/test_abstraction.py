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

import boto3
import bson
from moto import mock_ec2
# botocore has a client Stubber for mocking the error
from botocore.stub import Stubber
import sys, unittest
from unittest.mock import patch, Mock, MagicMock
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from mixer.backend.django import mixer
from poller.abstraction import abstractionLayer

sys.modules["bson"] = Mock()
sys.modules["boto3"] = Mock()


class TestAbstraction(TestCase):

    def setUp(self):
        self.client = Client()
        self.boto3_mock = sys.modules["boto3"]
        self.bson_mock = sys.modules["bson"].json_util
        self.ec2_mock = "ec2"
        self.health_mock = "health"
        self.region_mock = "eu-central-1"
        self.mock_roleArn = "mockArn:12345"

    @mock_ec2
    def test_client_spin_status_check_try_catch(self):
        
        # abstraction_scan_region_mock.return_value = mock_scanned_regions
        resources = boto3.resource(service_name="ec2", region_name="us-east-2")
        instance = resources.instances,all()
        print(instance)

        # instance = abstractionLayer(region)
        # instance.clientSpinStatusCheck(mock_extern_service, )

    # @patch("boto3.Instance")
    # @patch("boto3.ServiceResource")
    # @patch("poller.abstraction.abstractionLayer.scanRegion")
    # @patch("boto3.Session")
    # def test_client_spin_status_check_try_catch(self, session_mock, abstraction_scan_region_mock, resources_mock, instance_mock):
        
    #     region = self.region_mock
    #     mock_extern_service = self.ec2_mock

    #     mock_scanned_regions = {
    #                         'Regions': [
    #                             {
    #                                 'Endpoint': 'mock_endpoint_1',
    #                                 'RegionName': 'us-east-1',
    #                             },
    #                             {
    #                                 'Endpoint': 'mock_endpoint_2',
    #                                 'RegionName': 'us-east-2',
    #                             },
    #                             {
    #                                 'Endpoint': 'mock_endpoint_3',
    #                                 'RegionName': 'us-west-1',
    #                             },
    #                         ]
    #                     }
                    

    #     mock_tmp_credentials = [
    #         "mocked_aws_access_key_id",
    #         "mocked_aws_access_key_id",
    #         "mocked_aws_session_token",
        
    #     ]

    #     mock_resource_instances = [
    #             [
    #                 {
    #                 "instance_id": "mock_instance_id",
    #                 "type": "mock_type",
    #                 "platform": "mock_platform",
    #                 "kernel_id": "mock_kernel_id",
    #                 "hypervisor": "mock_hypervisor",
    #                 "root_device_name": "mock_device_name"

    #             },
    #         ]    
    #     ]

    #     abstraction_scan_region_mock.return_value = mock_scanned_regions
    #     resources_mock.return_value = mock_resource_instances
    #     # instance_mock.return_value = mock_resource_instances
    #     print(resources_mock)
    #     instance = abstractionLayer(region)
    #     instance.clientSpinStatusCheck(mock_extern_service, mock_tmp_credentials)