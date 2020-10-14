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
        self.region_mock = "us-east-2"
        self.mock_roleArn = "mockArn:12345"
         

    @patch("boto3.session.Session")
    @patch("botocore.client.BaseClient._make_api_call")
    @patch("boto3.client.describe_regions")
    def test_scan_region_try_catch(self, session_mock, client_mock, describe_regions_mock):
        region = self.region_mock
        # with self.assertRaises(SystemExit) as sys_exit:
        self.boto3_mock = Mock()
        session_mock.return_value = "boto3 client mocked "

        instance = abstractionLayer(region)
        instance.scanRegion(self.ec2_mock)

        # client_mock.assert_call_once('ec2')


    @patch("boto3.session.Session")
    @patch("boto3.client")
    def test_scan_region_exception_handling(self, session_mock, client_mock):
        region = self.region_mock
        with self.assertRaises(SystemExit) as sys_exit:
            self.boto3_mock = Mock()
            session_mock.return_value = "boto3 client mocked "

            instance = abstractionLayer(region)
            instance.scanRegion("us-east-2")

        self.assertEqual(sys_exit.exception.code, 1)


    @patch("boto3.session.Session")
    @patch("botocore.client.BaseClient._make_api_call")
    @patch("boto3.client.describe_events")
    def test_aws_health_try_catch(self, session_mock, client_mock, describe_events_mock):
        region = self.region_mock
        services = self.ec2_mock
        codes = "200"
        api = self.health_mock

        mock_response =  {'events': [
                    {
                        'arn': 'arn:health:1212',
                        'service': 'health',
                        'eventTypeCode': '200',
                        'eventTypeCategory': 'accountNotification',
                        'region': 'mock_region',
                        'statusCode': 'open',

                    },
                ],
            }

        self.boto3_mock = Mock()
        session_mock.return_value = "session for client mocked "

        # handling the try code block
        describe_events_mock.return_value = mock_response
        instance = abstractionLayer(region)
        instance.awshealth(api, region, services, codes)


    @patch("boto3.session.Session")
    @patch("botocore.client.BaseClient._make_api_call")
    def test_aws_health_exception_handling(self, session_mock, client_mock):
        
        region = self.region_mock
        services = ["ec2_mock", "s3_mock", "sts_mock"]
        codes = ["200", "302", "301"]
        
        with self.assertRaises(SystemExit) as sys_exit:
            self.boto3_mock = Mock()
            session_mock.return_value = "boto3 client mocked "

            # handling the try code block
            instance = abstractionLayer(region)
            instance.awshealth("health_mock", region, services, codes)

        self.assertEqual(sys_exit.exception.code, 1)

    @patch("boto3.session.Session")
    @patch("botocore.client.BaseClient._make_api_call")
    @patch("boto3.client.asssume_role")
    def test_aws_sts_role_try_catch(self, session_mock, client_mock, assume_role_mock):
        
        region = self.region_mock
        api = "sts"
        roleArn = self.mock_roleArn

        mock_response = {
                        'Credentials': {
                            'AccessKeyId': 'mock_access_id',
                            'SecretAccessKey': 'mock_access_secret',
                            'SessionToken': 'mock_session_token',
                            
                        },
                        'AssumedRoleUser': {
                            'AssumedRoleId': 'mock_id_1122Null',
                            'Arn': self.mock_roleArn
                        },
                        'PackedPolicySize': 123
                    }

        self.boto3_mock = Mock()
        session_mock.return_value = "session for boto3 client mocked "

        assume_role_mock.return_value = mock_response
        instance = abstractionLayer(region)
        instance.awsSTSRole(api, roleArn)

    @patch("boto3.session.Session")
    def test_aws_sts_role_exception_catch(self, session_mock):
        with self.assertRaises(SystemExit) as sys_exit:
            region = self.region_mock
            api = "sts"
            roleArn = ""

            instance = abstractionLayer(region)
            instance.awsSTSRole(api, roleArn)

        self.assertEqual(sys_exit.exception.code, 1)


    def test_role_data_extraction_try_catch(self):
        
        region = self.region_mock
        mock_credentials = {
            "Credentials" : {
                "AccessKeyId": "mocked_aws_access_key_id",
                "SecretAccessKey": "mocked_aws_access_secret",
                "SessionToken": "mocked_aws_session_token",

            }
        }

        instance = abstractionLayer(region)
        instance.roleDataExtraction(mock_credentials)


    def test_role_data_extraction_exception_handling(self):
        with self.assertRaises(SystemExit) as sys_exit:
            region = self.region_mock
            mock_credentials = {
                "Credentials" : {
                    "AccessKeyId": "mocked_aws_access_key_id",
                }
            }

            instance = abstractionLayer(region)
            instance.roleDataExtraction(mock_credentials)

        self.assertEqual(sys_exit.exception.code, 1)


    @patch("boto3.session.Session")
    @patch("botocore.client.BaseClient._make_api_call")
    @patch("boto3.client.describe_instances")
    def test_describe_instance_try_catch(self, session_mock, client_mock, describe_instances_mock):
        
        region = self.region_mock
        mock_extern_service = self.ec2_mock

        mock_credentials = [
                "mocked_aws_access_key_id",
                "mocked_aws_access_key_id",
                "mocked_aws_session_token",
            
        ]
        
        mock_response = {
                'Reservations': [
                    {
                        'Instances': [
                            {
                            'AmiLaunchIndex': 123,
                            'ImageId': 'mock_id',
                            'InstanceId': 'mock_instance_id',
                            'InstanceType': 't1.micro',
                            'KernelId': 'mock_kernel_id',
                            'KeyName': 'mock_instance_tester',
                            'Monitoring': {
                                'State': 'disabled'
                            },
                            'Placement': {
                                'AvailabilityZone': 'us-east-2',
                                'Affinity': 'mock_high',
                                'PartitionNumber': 123,
                                'HostId': 'mock_host_id',
                                'Tenancy': 'dedicated',
                                'SpreadDomain': 'mock_spread_domain',
                                'HostResourceGroupArn': 'mock_host_resource_arn'
                                },
                            }
                        ]
                    }
                ]
            }

        session_mock.return_value = "session for boto3 client is mocked "
        describe_instances_mock.return_value = mock_response

        instance = abstractionLayer(region)
        instance.describeInstance(mock_extern_service, mock_credentials)

    
    def test_describe_instance_outer_exception_handling(self, ):
        with self.assertRaises(SystemExit) as sys_exit:
            region = self.region_mock
            mock_extern_service = self.ec2_mock
            
            mock_tmp_credentials = [
                "mocked_aws_access_key_id",
                "mocked_aws_access_key_id",
            
                ]

            instance = abstractionLayer(region)
            instance.describeInstance(mock_extern_service, mock_tmp_credentials)
        
        self.assertEqual(sys_exit.exception.code, 1)


    @patch("boto3.session.Session")
    def test_describe_instance_inner_exception_handling(self, session_mock):
        with self.assertRaises(SystemExit) as sys_exit:

            region = self.region_mock
            mock_extern_service = self.ec2_mock
            
            mock_tmp_credentials = [
                "mocked_aws_access_key_id",
                "mocked_aws_access_key_id",
                "mocked_aws_session_token",
            
                ]

            instance = abstractionLayer(region)
            instance.describeInstance(mock_extern_service, mock_tmp_credentials)
        
        self.assertEqual(sys_exit.exception.code, 1)

    """
        
        # testcase for client spin status check try block

    """
    def test_client_spin_status_outer_exception_handling(self, ):
        with self.assertRaises(SystemExit) as sys_exit:
            region = self.region_mock
            mock_extern_service = self.ec2_mock
            
            mock_tmp_credentials = [
                "mocked_aws_access_key_id",
                "mocked_aws_access_key_id",
            
                ]

            instance = abstractionLayer(region)
            instance.clientSpinStatusCheck(mock_extern_service, mock_tmp_credentials)
        
        self.assertEqual(sys_exit.exception.code, 1)


    @patch("boto3.session.Session")
    def test_client_spin_status_inner_exception_handling(self, session_mock):
        with self.assertRaises(SystemExit) as sys_exit:

            region = self.region_mock
            mock_extern_service = self.ec2_mock
            
            mock_tmp_credentials = [
                "mocked_aws_access_key_id",
                "mocked_aws_access_key_id",
                "mocked_aws_session_token",
            
                ]

            instance = abstractionLayer(region)
            instance.clientSpinStatusCheck(mock_extern_service, mock_tmp_credentials)
        
        self.assertEqual(sys_exit.exception.code, 1)

