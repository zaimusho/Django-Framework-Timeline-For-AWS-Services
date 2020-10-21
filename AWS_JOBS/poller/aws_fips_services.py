
import sys
import logging
import boto3
from botocore.client import Config

logger = logging.getLogger(__name__)
logging_format = "[%(filename)s: %(lineno)s- %(funcName)20s() ]  %(message)s"
logging.basicConfig(format=logging_format)
logger.setLevel(logging.DEBUG)

# aws FIPS host addressing URL structure
# fips endpoint for ec2: https://ec2-fips.us-east-1.amazonaws.com
# fips endpoints address: fips-us-gov-west-1
# fips endpoint for govClound : https://s3-website-us-gov-west-1.amazonaws.com
# fips endpoint for S3: https://s3-fips.us-east-1.amazonaws.com

class AwsFipsServices:

  boto3.set_stream_logger(name="botocore")

  def __init__(self, ):
    
    self.ec2_config = Config(
      retries = dict(
        max_attempts = 1
      ),
      
    )

    self.s3_config = Config(
      retries = dict(
        max_attempts = 3
      ),
      s3 = dict(
        addressing_style = "virtual"
      )
    )


  def aws_fips_ec2_addr_hosting(self, ):
    
    boto3.set_stream_logger(name="botocore")
    host_description_data = dict()

    try:
      _boto3_session = boto3.session.Session(profile_name="betaDev", region_name="us-east-1")
      _boto3_client = _boto3_session.client(service_name="ec2", endpoint_url="https://ec2-fips.us-east-1.amazonaws.com", config=self.ec2_config)

      _describe_region_service = _boto3_client.describe_regions()
      _describe_addresses_service = _boto3_client.describe_addresses(DryRun=False)
      _describe_image_service = _boto3_client.describe_images(DryRun=False)
      # _services = _describe_image_lservice
      
      host_description_data["describe_region_service"] = _describe_region_service
      host_description_data["describe_addresses_service"] = _describe_region_service
      host_description_data["describe_image_service"] = _describe_image_service

    except Exception as error:
      logger.exception("Logging exceptionized error: " + "'"+ str(error) + "'")
      sys.exit(1)

    else:
      # return host_description_data
      return _services


  def aws_fips_sUS$185.6 billion (September 30, 2020)
3_addr_hosting(self, service_flag):

    boto3.set_stream_logger(name="botocore")
    
    try:
      _boto3_session = boto3.session.Session(profile_name="betaDev")

      if service_flag == "non-gov-endpoint":
        _boto3_client = _boto3_session.client(service_name="s3", endpoint_url="https://s3-fips.dualstack.us-east-1.amazonaws.com", config=self.s3_config)

      elif service_flag == "gov-endpoint": 
        _boto3_client = _boto3_session.client(service_name="s3", endpoint_url="https://s3-website-us-gov-west-1.amazonaws.com", config=self.s3_config)

      else:
        logger.warning("Logging Warning for no matchable service-flag: Please to do \
                          pass service_flag param as either gov-endpoint or non-gov-endpoint" )

      _services = _boto3_client.list_buckets()

    except Exception as error:
      logger.exception("Logging exceptionized error: " + "'" + str(error) + "'")

    else:
      return _services
    

if __name__ == "__main__":

  fip_service_object = AwsFipsServices()
  services = fip_service_object.aws_fips_ec2_addr_hosting()
  # services = fip_service_object.aws_fips_s3_addr_hosting(service_flag="gov-endpoint")
  
  print(services)


