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

import boto3
import unittest
from poller.abstraction import abstractionLayer
from moto import mock_ec2
from django.test import TestCase

class TestAbstractionSpinClientMethod(TestCase):

    def setUp(self):
        self.region = "us-east-2"
        self.extern_service = "ec2"
        self.temp_credentials = [
            "mock_aws_access_key_id",
            "mock_aws_secret_access_key",
            "mock_aws_session_access_token"

        ]


    @mock_ec2
    def test_boto3_describe_regions(self):
        ec2 = boto3.client("ec2", "us-east-1")
        resp = ec2.describe_regions()
        len(resp["Regions"]).should.be.greater_than(1)
        for rec in resp["Regions"]:
            rec["Endpoint"].should.contain(rec["RegionName"])

        test_region = "us-east-1"
        resp = ec2.describe_regions(RegionNames=[test_region])
        resp["Regions"].should.have.length_of(1)
        resp["Regions"][0].should.have.key("RegionName").which.should.equal(test_region)
        resp["Regions"][0].should.have.key("OptInStatus").which.should.equal(
            "opt-in-not-required"
        )

        test_region = "ap-east-1"
        resp = ec2.describe_regions(RegionNames=[test_region])
        resp["Regions"].should.have.length_of(1)
        resp["Regions"][0].should.have.key("RegionName").which.should.equal(test_region)
        resp["Regions"][0].should.have.key("OptInStatus").which.should.equal("not-opted-in")

    
    @mock_ec2
    def test_client_spin_status_check_try_catch(self):
        objInstance = abstractionLayer(self.region)

        conn = boto3.client("ec2", "us-east-1")
        region = conn.describe_regions()
        connect = conn.resource(self.extern_service, region_name=self.region)
        scannedRegion = ["us-east-1", "us-east-2", "us-west-1"]
        instance = connect.instances.all()
        objInstance.clientSpinStatusCheck(self.extern_service, self.temp_credentials)
        print(region)
        print(instance)
