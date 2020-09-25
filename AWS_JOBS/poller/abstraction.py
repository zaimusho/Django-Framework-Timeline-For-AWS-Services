
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


class awsClass:
  
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
      exit()
    
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
      exit()
      
  def awsSTSRole(self, apiCall, roleARN): #, **policyJSON):
    
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
        # Policy= str(policyJSON['policyJSON']),
        ExternalId= 'assumeRoleAWS'
      )
      
      logger.info(assumeRole)
      
    except  Client.exceptions.MalformedPolicyDocumentException as endPointErr:
      logger.exception("Logging Exception: "+ str(endPointErr)+ "\n")
      raise
      exit()
      
    else:
      return assumeRole
  
  def roleDataExtraction(self, assumeRoleCredentials): #, filePath):
    
    # extracting credentials from the Roles created in particular session
    tmpCredentials = list()
    
    try:
      # objFile = open(filePath, "r")
      # policyJSON = json.load(objFile)
       
      # unpacking the id, secret and security token
    
      tmpCredentials.append(assumeRoleCredentials['Credentials']['AccessKeyId'])
      tmpCredentials.append(assumeRoleCredentials['Credentials']['SecretAccessKey']) 
      tmpCredentials.append(assumeRoleCredentials['Credentials']['SessionToken'])
      
      # objFile.close()
      
      logger.info("Temporary Credentials Retrieved")
      # return assumeRoleSTSCredentials
      
    except NoCredentialsError as credsErr:
      logger.exception("Logging exception: "+ str(credsErr)+ "\n")
      raise
      exit()
      
    else:
      return tmpCredentials
      
  # Use the assumed clients temporary security credentials to spin new Boto3 client instance
  
  def clientSpinStatusCheck(self, externService, tmpCredentials):
    
    # Executing the client using STS credentails
    response= dict()
    flag = False

    try:
      if tmpCredentials:
        securityID = tmpCredentials[0]
        securitySecret = tmpCredentials[1]
        securityToken = tmpCredentials[2]
        
        # print(securityID, securitySecret, securityToken)
        session = boto3.Session(region_name=self.REGION)
        logger.info(session)
        
        assumedClient = session.client(service_name=externService, 
                                      aws_access_key_id = securityID, 
                                      aws_secret_access_key = securitySecret,
                                      aws_session_token = securityToken,)
        
        # assumedClient = session.client(service_name=externService)
        
        logger.info(assumedClient)
        
        try:
          # scanning the AWS regions for entire spinned instances
          scannedRegion = self.scanRegion(service=externService)
          logger.info("Listing the AWS instances Region Worldwide")
          
          for eachRegion in scannedRegion['Regions']:
            # allRegions.append(eachRegion['RegionName'])
            session = boto3.Session(profile_name="development", region_name=eachRegion["RegionName"])
            logger.info("Iterated session Object " + str(session) + "\n")
            fetchResource = session.resource(service_name=externService)
            
            for eachInstance in fetchResource.instances.all():
              print(eachInstance.instance_id, eachInstance.instance_type, eachInstance.instance_lifecycle, eachInstance.platform, 
                    eachInstance.hypervisor, eachInstance.architecture, eachInstance.root_device_name, eachInstance.iam_instance_profile,
                    eachInstance.launch_time, eachInstance.placement, eachInstance.state, eachInstance.state_transition_reason, 
                    eachInstance.ami_launch_index, eachInstance.client_token, eachInstance.image, eachInstance.network_interfaces, 
                    eachInstance.metadata_options, eachInstance.state_reason, eachInstance.network_interfaces_attribute, 
                    "\n")            
            
          logger.info("Variable components of AWS instance Acquired !")
           
        except Exception as err:
          logger.exception("Logging externService exception: "+ str(err)+ "\n")
          raise
        
        
        if flag:
          try:
            if externService == "ec2":
              # explicity defining the system, internal state of running instances
              response = assumedClient.describe_instance_status(IncludeAllInstances=True, DryRun=False)
              # response = assumedClient.describe_instances(DryRun=False)
              logging.debug(response)
            
          except Exception as err:
            logger.exception("Logging externService exception: "+ str(err)+ "\n")
            exit()
            
          
          else:
            return response
            
    except Exception as outerErr:
      logger.exception("Logging exception error for Spin New Client method: "+ str(outerErr)+ "\n")
      raise
      exit()    
    
     
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
      exit()
