
import os, sys
import boto3
import boto3.session
import logging
import pprint, json
from bson import json_util
from botocore.exceptions import NoCredentialsError, InvalidSTSRegionalEndpointsConfigError

# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger(__name__)
logging_format = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=logging_format)
logger.setLevel(logging.DEBUG)


class AbstractionLayer:
  
  def __init__(self, region):
    super(AbstractionLayer, self).__init__()
    self.region = region
   
  # Instead of taking the aws credentials explicity (profile_name="betaDev")
  # this can be defined implicity as (aws_access_key_id, aws_secret_access_key) 
  
  def scan_region(self, service):
    try:
      # scan AWS Regions available for services
      session_obj = boto3.session.Session(profile_name="betaDev", region_name=self.region)
      logger.info("Session Object: " + str(session_obj))
      client = session_obj.client(service_name=service)
      logger.info(client)
      service_regions = client.describe_regions()
      
    except Exception as error:
      logger.exception(str(error))
      # raise
      sys.exit(1)
    
    else:
      return service_regions
   
    
  def aws_health(self, api_call, polling_region, services, status_codes):
    # describe affected entities
    # management by access
    try:
      session = boto3.session.Session(profile_name="betaDev", region_name=polling_region)
      client = session.client(api_call)
      logger.info(client)
      
      # print(self.REGION)
      health_response = client.describe_events(
                filter = {
                  'services': services,
                  'eventStatusCodes': status_codes
                }
              )
      
      logger.info(str(health_response))
      
      return health_response
    
    except Exception as err:
      logger.warning("Logging Exception: "+ str(err)+ "\n")
      sys.exit(1)
      
      
  def aws_sts_role(self, api_call, role_arn):
    
    try:
      # experimenting the aws STS roles configurations
      session = boto3.session.Session(profile_name="betaDev", region_name=self.region)
      # Session = boto3.Session(region_name=self.REGION)
      client = session.client(api_call)
      
      logger.debug(client)
      assume_role = client.assume_role(
        RoleArn= role_arn,
        RoleSessionName= 'AssumeRoleSession',
        PolicyArns=[
                    {
                      "arn": "arn:aws:iam::179790312905:policy/AWS_AssumeRolePolicy"
                    },
                  ],
        ExternalId= 'assumeRoleAWS'
      )
      
      logger.info(assume_role)
      
    except Exception as end_point_err:
      logger.exception("Logging Exception: "+ str(end_point_err)+ "\n")
      # raise
      sys.exit(1)
      
    else:
      return assume_role
  
  
  def role_data_extraction(self, assume_role_credentials):
    # extracting credentials from the Roles created in particular session
    temp_credentials = list()
    
    try: 
      # unpacking the id, secret and security token
    
      temp_credentials.append(assume_role_credentials['Credentials']['AccessKeyId'])
      temp_credentials.append(assume_role_credentials['Credentials']['SecretAccessKey']) 
      temp_credentials.append(assume_role_credentials['Credentials']['SessionToken'])
      
      logger.info("Temporary Credentials Retrieved")
      
    except Exception as creds_err:
      logger.exception("Logging exception: "+ str(creds_err)+ "\n")
      # raise
      sys.exit(1)
      
    else:
      return temp_credentials
      
  
  # Use the assumed clients temporary security credentials to spin new Boto3 client instance
  
  def client_spin_status_check(self, extern_service, temp_credentials):
    
    # Executing the client using STS temporary credentails
    instance = dict()
    instance_stack = list()
    # flag = False
    try:
      if temp_credentials:
        security_id = temp_credentials[0]
        security_secret = temp_credentials[1]
        security_token = temp_credentials[2]
        
        # print(securityID, securitySecret, securityToken)
        
        try:
          # scanning the AWS regions for entire spinned instances
          scanned_region = self.scan_region(service=extern_service)
          logger.info("Listing the AWS instances Region Worldwide")
          
          for each_region in scanned_region['Regions']:
            # allRegions.append(eachRegion['RegionName'])
            session = boto3.session.Session(aws_access_key_id = security_id, 
                                    aws_secret_access_key = security_secret,
                                    aws_session_token = security_token, 
                                    region_name=each_region["RegionName"])
            
            logger.info("Iterated session Object " + str(session) + "\n")
            fetch_resource = session.resource(service_name=extern_service)
            print("fetch resources type ", fetch_resource)
            
            for each_instance in fetch_resource.instances.all():
              print("each instance", each_instance)
              # inline response catch for the instance history
              print(each_instance.instance_id, each_instance.instance_type, each_instance.platform, 
                    each_instance.hypervisor, each_instance.architecture, each_instance.root_device_name, each_instance.iam_instance_profile,
                    each_instance.launch_time, each_instance.placement, each_instance.state, each_instance.state_transition_reason, 
                    each_instance.ami_launch_index, each_instance.client_token, each_instance.image, each_instance.network_interfaces, 
                    each_instance.metadata_options, each_instance.state_reason, each_instance.network_interfaces_attribute, 
                    "\n")            
           
              instance = {
                "instanceId": each_instance.instance_id,
                "type": each_instance.instance_type,
                "platform": each_instance.platform,
                "kernelId": each_instance.kernel_id,
                "hypervisor": each_instance.hypervisor,
                "architecture": each_instance.architecture,
                "rootDevice": each_instance.root_device_name,
                "lauchtime": each_instance.launch_time.strftime("%Y-%m-%d %I:%M %p"),
                "state": each_instance.state,
                "tranReason": each_instance.state_transition_reason,
                "ami_index": each_instance.ami_launch_index,
                "clientToken": each_instance.client_token,
                "hibernation": each_instance.hibernation_options["Configured"],
                "ebs": each_instance.ebs_optimized,
                "image": each_instance.image,
                "interface": each_instance.network_interfaces[0],
                "stateReason": each_instance.state_reason["Message"],
                "groupId": (each_instance.network_interfaces_attribute[0]["Groups"])[0]["GroupId"],
                "MacAddress": each_instance.network_interfaces_attribute[0]["MacAddress"],
                "ownerId": each_instance.network_interfaces_attribute[0]["OwnerId"],
                "privateIpAddr": each_instance.network_interfaces_attribute[0]["PrivateIpAddress"],
                "networkStatus": each_instance.network_interfaces_attribute[0]["Status"],
                "httpEndpoint": each_instance.metadata_options["HttpEndpoint"],
                "placementZone": each_instance.placement["AvailabilityZone"],
                "tenancy": each_instance.placement["Tenancy"],
                "Arn": each_instance.iam_instance_profile["Arn"],
                "ArnId": each_instance.iam_instance_profile["Id"],
                "status": each_instance.state["Name"],
                "statusCode": each_instance.state["Code"],
                
              }
              
              instance_stack.append(instance)
              
              logger.info("Information logged for AWS region: {}" .format(each_region["RegionName"]) + "\n")
              
          logger.info("Variable components of AWS instance Acquired !")
           
        except Exception as err:
          logger.exception("Logging externService exception: "+ str(err)+ "\n")
          # raise
          sys.exit(1)
        else:
          return instance_stack
            
    except Exception as outer_err:
      logger.exception("Logging exception error for Spin New Client method: "+ str(outer_err)+ "\n")
      # raise
      sys.exit(1)    
    
     
  def describe_instance(self, extern_service, temp_credentials):
    # Executing the client using STS temporary credentails
    response = dict()
    flag = True

    try:
      if temp_credentials:
        security_id = temp_credentials[0]
        security_secret = temp_credentials[1]
        security_token = temp_credentials[2]
        
        # print(securityID, securitySecret, securityToken)
        session = boto3.session.Session(region_name=self.region)
        logger.info(session)
        
        # Client session for flag condition block 
        assumed_client = session.client(service_name=extern_service, 
                                      aws_access_key_id = security_id, 
                                      aws_secret_access_key = security_secret,
                                      aws_session_token = security_token)
        
        # assumedClient = session.client(service_name=externService)
        
        logger.info(assumed_client)
        
        if flag:
          try:
            if extern_service == "ec2":
              # explicity defining the system, internal state of running instances
              # response = assumedClient.describe_instance_status(IncludeAllInstances=True, DryRun=False)
              response = assumed_client.describe_instances(DryRun=False)
              logging.debug(response)
            
          except Exception as err:
            logger.exception("Logging externService exception: "+ str(err)+ "\n")
            sys.exit(1)
            
          
          else:
            return response
      
    except Exception as outer_err:
      logger.exception("Logging exception error for Spin New Client method: "+ str(outer_err)+ "\n")
      # raise
      sys.exit(1)  
  
  '''
  
  # not used for the while as this to be used in consideration with other 
  # defined scope

  # def decode_auth_message(self):
    
  #   # encoding method call for authorisation message
  #   session = boto3.session.Session(profile_name="betaDev", region_name=self.region)
  #   client = session.client('sts')
  #   logger.debug(client)
    
  #   try:
  #     sts_session = client
  #     auth_response = sts_session.decode_authorisation_message(
  #       EncodedMessage= 'initial encoding authorisation message response', # message of interest that needs to be encoded
  #     )
      
  #     logger.info(str(auth_response))
      
  #     return auth_response
      
  #   except client.exceptions.InvalidAuthorizationMessageException as auth_message_err:
  #     logger.warn("Logging Exception: "+ str(auth_message_err)+ "\n")
  #     sys.exit(1)



  # handling of raise exceptions needs to be practiced for scripting
  # testcases for exception raising.

  '''