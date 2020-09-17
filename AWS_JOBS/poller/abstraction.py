
import os, sys
import boto3
import logging
import pprint, json
from bson import json_util
from botocore.exceptions import NoCredentialsError, InvalidSTSRegionalEndpointsConfigError

# logging proc structure for the valid executable script and throwable exception

logger = logging.getLogger('root')
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
      sessionObj = boto3.Session(profile_name="development", region_name=self.REGION)
      logger.info("Session Object: " + str(sessionObj))
      client = sessionObj.client(service_name=service)
      logger.info(client)
      serviceRegions = client.describe_regions()
      
      return serviceRegions
    
    except Exception as error:
      logger.warn(str(error))
      exit()
    
  def awshealth(self, apiCall, pollingRegion, services, *statusCodes):
    # describe affected entities
    # management by access
    
    Session = boto3.Session(profile_name="development", region_name=pollingRegion)
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
    Session = boto3.Session(profile_name="development", region_name=self.REGION)
    Client = Session.client(apiCall)
    logger.debug(Client)
    
    try:
      assumeRole = Client.assume_role(
        RoleArn= roleARN,
        RoleSessionName= 'newSession',
        PolicyArns=[
                    {
                      "arn": "arn:aws:iam::179790312905:policy/STS"
                    },
                  ],
        # Policy= str(policyJSON['policyJSON']),
        ExternalId= 'assumeRoleAWS'
      )
      
      logger.info(roleARN)
      
      return assumeRole
      
    except  Client.exceptions.MalformedPolicyDocumentException as endPointErr:
      logger.warn("Logging Exception: "+ str(endPointErr)+ "\n")
      return str(endPointErr)
      exit()

  def roleDataExtraction(self, apiCall, roleARN): #, filePath):
    
    # extracting credentials from the Roles created in particular session
    
    try:
      # objFile = open(filePath, "r")
      # policyJSON = json.load(objFile)
      
      assumeRoleSTSCredentials = self.awsSTSRole(apiCall=apiCall, roleARN=roleARN) #, policyJSON=policyJSON)
      
      # unpacking the id, secret and security token
    
      securityID = assumeRoleSTSCredentials['Credentials']['AccessKeyId']
      securitySecret = assumeRoleSTSCredentials['Credentials']['SecretAccessKey'] 
      securityToken = assumeRoleSTSCredentials['Credentials']['SessionToken']
      
      # objFile.close()
      
      return (securityID, securitySecret, securityToken)
      # return assumeRoleSTSCredentials
      
    except NoCredentialsError as credsErr:
      logger.warn("Logging exception: "+ str(credsErr)+ "\n")
      return str(credsErr)
      exit()
      
  # Use the assumed clients temporary security credentials to spin new Boto3 client instance
  
  def spinNewClient(self, apiCall, *tmpCredentials):
    
    # Executing the client using STS credentails
    
    securityID = tmpCredentials[0]
    securitySecret = tmpCredentials[1]
    securityToken = tmpCredentials[2]
    session = boto3.Session(profile_name="development", region_name=self.REGION)
    assumedClient = boto3.client(service_name=apiCall, aws_access_key_id = securityID, 
                                aws_secret_acces_key = securitySecret,
                                aws_session_token = securityToken)
    
    logging.debug(assumedClient)
    
    if apiCall == "ec2":
      response = assumedClient.describe_instance_status(IncludeAllInstances=True)
      logging.debug(response)
    
    return response
    
    
  def decodeAuthMessage(self):
    
    # encoding method call for authorisation message
    session = boto3.Session(profile_name="development", region_name=self.REGION)
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
