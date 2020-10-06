
import os, sys
import boto3
import logging
import pprint, json
from bson import json_util
from botocore.exceptions import NoCredentialsError, InvalidSTSRegionalEndpointsConfigError

# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger(__name__)
loggingFormat = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=loggingFormat)
logger.setLevel(logging.DEBUG)


class abstractionLayer:
  
  def __init__(self, REGION):
    super().__init__()
    self.REGION = REGION
   
    
  def scanRegion(self, service):
    try:
      # scan AWS Regions available for services
      sessionObj = boto3.Session(profile_name="betaDev", region_name=self.REGION)
      logger.info("Session Object: " + str(sessionObj))
      client = sessionObj.client(service_name=service)
      logger.info(client)
      serviceRegions = client.describe_regions()
      
    except Exception as error:
      logger.exception(str(error))
      raise
      sys.exit(1)
    
    else:
      return serviceRegions
   
    
  def awshealth(self, apiCall, pollingRegion, services, *statusCodes):
    # describe affected entities
    # management by access
    
    Session = boto3.Session(profile_name="betaDev", region_name=pollingRegion)
    Client = Session.client(apiCall)
    logger.info(Client)
    
    try:
      
      # print(self.REGION)
      healthResponse = Client.describe_events(
                filter = {
                  'services': services,
                  'eventStatusCodes': statusCodes
                }
              )
      
      logger.info(str(healthResponse))
      
      return healthResponse
    
    except Client.exceptions.InvalidPaginationToken as err:
      logger.warn("Logging Exception: "+ str(err)+ "\n")
      return str(err)
      sys.exit(1)
      
      
  def awsSTSRole(self, apiCall, roleARN):
    
    # experimenting the aws STS roles configurations
    Session = boto3.Session(profile_name="betaDev", region_name=self.REGION)
    # Session = boto3.Session(region_name=self.REGION)
    Client = Session.client(apiCall)
    
    logger.debug(Client)
    
    try:
      assumeRole = Client.assume_role(
        RoleArn= roleARN,
        RoleSessionName= 'aAssumeRoleSession',
        PolicyArns=[
                    {
                      "arn": "arn:aws:iam::179790312905:policy/AWS_AssumeRolePolicy"
                    },
                  ],
        ExternalId= 'assumeRoleAWS'
      )
      
      logger.info(assumeRole)
      
    except  Client.exceptions.MalformedPolicyDocumentException as endPointErr:
      logger.exception("Logging Exception: "+ str(endPointErr)+ "\n")
      raise
      sys.exit(1)
      
    else:
      return assumeRole
  
  
  def roleDataExtraction(self, assumeRoleCredentials):
    # extracting credentials from the Roles created in particular session
    tmpCredentials = list()
    
    try: 
      # unpacking the id, secret and security token
    
      tmpCredentials.append(assumeRoleCredentials['Credentials']['AccessKeyId'])
      tmpCredentials.append(assumeRoleCredentials['Credentials']['SecretAccessKey']) 
      tmpCredentials.append(assumeRoleCredentials['Credentials']['SessionToken'])
      
      logger.info("Temporary Credentials Retrieved")
      
    except NoCredentialsError as credsErr:
      logger.exception("Logging exception: "+ str(credsErr)+ "\n")
      raise
      sys.exit(1)
      
    else:
      return tmpCredentials
      
  
  # Use the assumed clients temporary security credentials to spin new Boto3 client instance
  
  def clientSpinStatusCheck(self, externService, tmpCredentials):
    
    # Executing the client using STS temporary credentails
    response, instance = dict(), dict()
    instanceStack = list()
    flag = False

    try:
      if tmpCredentials:
        securityID = tmpCredentials[0]
        securitySecret = tmpCredentials[1]
        securityToken = tmpCredentials[2]
        
        # print(securityID, securitySecret, securityToken)
        
        try:
          # scanning the AWS regions for entire spinned instances
          scannedRegion = self.scanRegion(service=externService)
          logger.info("Listing the AWS instances Region Worldwide")
          
          for eachRegion in scannedRegion['Regions']:
            # allRegions.append(eachRegion['RegionName'])
            
            session = boto3.Session(aws_access_key_id = securityID, 
                                    aws_secret_access_key = securitySecret,
                                    aws_session_token = securityToken, 
                                    region_name=eachRegion["RegionName"])
            
            
            logger.info("Iterated session Object " + str(session) + "\n")
            fetchResource = session.resource(service_name=externService)
            
            for eachInstance in fetchResource.instances.all():
              # inline response catch for the instance history
              
              print(eachInstance.instance_id, eachInstance.instance_type, eachInstance.platform, 
                    eachInstance.hypervisor, eachInstance.architecture, eachInstance.root_device_name, eachInstance.iam_instance_profile,
                    eachInstance.launch_time, eachInstance.placement, eachInstance.state, eachInstance.state_transition_reason, 
                    eachInstance.ami_launch_index, eachInstance.client_token, eachInstance.image, eachInstance.network_interfaces, 
                    eachInstance.metadata_options, eachInstance.state_reason, eachInstance.network_interfaces_attribute, 
                    "\n")            
           
              instance = {
                "instanceId": eachInstance.instance_id,
                "type": eachInstance.instance_type,
                "platform": eachInstance.platform,
                "kernelId": eachInstance.kernel_id,
                "hypervisor": eachInstance.hypervisor,
                "architecture": eachInstance.architecture,
                "rootDevice": eachInstance.root_device_name,
                "lauchtime": eachInstance.launch_time.strftime("%Y-%m-%d %I:%M %p"),
                "state": eachInstance.state,
                "tranReason": eachInstance.state_transition_reason,
                "ami_index": eachInstance.ami_launch_index,
                "clientToken": eachInstance.client_token,
                "hibernation": eachInstance.hibernation_options["Configured"],
                "ebs": eachInstance.ebs_optimized,
                "image": eachInstance.image,
                "interface": eachInstance.network_interfaces[0],
                "stateReason": eachInstance.state_reason["Message"],
                "groupId": (eachInstance.network_interfaces_attribute[0]["Groups"])[0]["GroupId"],
                "MacAddress": eachInstance.network_interfaces_attribute[0]["MacAddress"],
                "ownerId": eachInstance.network_interfaces_attribute[0]["OwnerId"],
                "privateIpAddr": eachInstance.network_interfaces_attribute[0]["PrivateIpAddress"],
                "networkStatus": eachInstance.network_interfaces_attribute[0]["Status"],
                "httpEndpoint": eachInstance.metadata_options["HttpEndpoint"],
                "placementZone": eachInstance.placement["AvailabilityZone"],
                "tenancy": eachInstance.placement["Tenancy"],
                "Arn": eachInstance.iam_instance_profile["Arn"],
                "ArnId": eachInstance.iam_instance_profile["Id"],
                "status": eachInstance.state["Name"],
                "statusCode": eachInstance.state["Code"],
                
              }
              
              instanceStack.append(instance)
              
              logger.info("Information logged for AWS region: {}" .format(eachRegion["RegionName"]) + "\n")
              
          logger.info("Variable components of AWS instance Acquired !")
           
        except Exception as err:
          logger.exception("Logging externService exception: "+ str(err)+ "\n")
          raise
        
        else:
          return instanceStack
            
    except Exception as outerErr:
      logger.exception("Logging exception error for Spin New Client method: "+ str(outerErr)+ "\n")
      raise
      sys.exit(1)    
    
     
  def describeInstance(self, externService, tmpCredentials):
    # Executing the client using STS temporary credentails
    response = dict()
    flag = True

    try:
      if tmpCredentials:
        securityID = tmpCredentials[0]
        securitySecret = tmpCredentials[1]
        securityToken = tmpCredentials[2]
        
        # print(securityID, securitySecret, securityToken)
        session = boto3.Session(region_name=self.REGION)
        logger.info(session)
        
        # Client session for flag condition block 
        assumedClient = session.client(service_name=externService, 
                                      aws_access_key_id = securityID, 
                                      aws_secret_access_key = securitySecret,
                                      aws_session_token = securityToken)
        
        # assumedClient = session.client(service_name=externService)
        
        logger.info(assumedClient)
        
        if flag:
          try:
            if externService == "ec2":
              # explicity defining the system, internal state of running instances
              # response = assumedClient.describe_instance_status(IncludeAllInstances=True, DryRun=False)
              response = assumedClient.describe_instances(DryRun=False)
              logging.debug(response)
            
          except Exception as err:
            logger.exception("Logging externService exception: "+ str(err)+ "\n")
            sys.exit(1)
            
          
          else:
            return response
      
    except Exception as outerErr:
      logger.exception("Logging exception error for Spin New Client method: "+ str(outerErr)+ "\n")
      raise
      sys.exit(1)  
  
  
  def decodeAuthMessage(self):
    
    # encoding method call for authorisation message
    session = boto3.Session(profile_name="betaDev", region_name=self.REGION)
    Client = session.client('sts')
    logger.debug(Client)
    
    try:
      stsSession = Client
      authResponse = stsSession.decode_authorisation_message(
        EncodedMessage= 'initial encoding authorisation message response', # message of interest that needs to be encoded
      )
      
      logger.info(str(authResponse))
      
      return authResponse
      
    except Client.exceptions.InvalidAuthorizationMessageException as authMessageErr:
      logger.warn("Logging Exception: "+ str(authMessageErr)+ "\n")
      return str(authMessageErr)
      sys.exit(1)
