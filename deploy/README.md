
# DEPLOY

Although these Cloudformation templates are meant to serve more as a reference, you can indeed deploy them directly.  

The templates prefixed with **"existing-stack"** are generally more indicative of how we expect customers to deploy Big-IPs (insertion into an existing environment).

However, as a convenience, we include additional templates:

 - **"full-stack":** creates a full example deployment (VPC, subnets, route-tables, security groups, sample webserver and a Big-IP) so you can quickly have a complete working environment from scratch to explore.
 - **"infra-only":** creates a VPC, subnet, route-tables, webserver, and security groups.   
 - **"network-only":** creates a VPC, subnets, route-tables.
 - **"security-groups":** creates reference security groups.


## Quickstart

Go to the marketplace and accept the user agreement for the version being launched.
 
If you are new to AWS, we recommend running a full-stack template as that will give you a full working environment you can inspect

ex.
[full-stack-hourly-1nic-bigip.template](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/experimental/standalone/1nic/learning-stack/payg/f5-full-stack-payg-1nic-bigip.template)


If you are familiar with AWS and have an existing stack, we recommend first trying:

[existing-stack-hourly-1nic-bigip.template](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/experimental/standalone/1nic/existing-stack/payg/f5-existing-stack-payg-1nic-bigip-w-waf.template)

and taking a look at:

[security-groups-for-1nic-bigip.template](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/experimental/reference/2nic/security-group-creation/f5-security-groups-for-2nic-bigip.template)

to know which ports to enable.

*NOTE: Advanced templates require increased service limits (ex. EIPs) so make account has sufficient resources. You can open a ticket with AWS to increase your limits*


## Example of deploying stacks through aws cli:

For more information re: installing the aws cli:

http://docs.aws.amazon.com/cli/latest/userguide/installing.html

 1. cd into directory containing templates
 2. run relevant command below


###1 NIC:

####Full Stack - BYOL:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://f5-full-stack-payg-1nic-bigip.template 
    --stack-name full-stack-bigip-1nic
    --parameters  
    ParameterKey=sshKey,ParameterValue=YOUR-SSH-KEY
    ParameterKey=availabilityZone1,ParameterValue=us-west-2a
    ParameterKey=availabilityZone2,ParameterValue=us-west-2b
    ParameterKey=bigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=bigipPerformanceType,ParameterValue=Good
    ParameterKey=webserverInstanceType,ParameterValue=t1.micro
    ParameterKey=bigipAdminUsername,ParameterValue=admin
    ParameterKey=bigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=bigipManagementGuiPort,ParameterValue=443
    ParameterKey=bigip1LicenseKey,ParameterValue=LUFJD-YREAG-VQHVI-EYOQH-JBBKXAI

####Existing Stack - BYOL:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://existing-stack-byol-1nic-bigip.template
    --stack-name existing-stack-bigip-1nic
    --parameters  
    ParameterKey=sshKey,ParameterValue=YOUR-SSH-KEY
    ParameterKey=bigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=bigipPerformanceType,ParameterValue=Good
    ParameterKey=bigipAdminUsername,ParameterValue=admin
    ParameterKey=bigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=bigipManagementGuiPort,ParameterValue=443
    ParameterKey=vpc,ParameterValue=vpc-61a94705
    ParameterKey=az1ExternalSubnet,ParameterValue=subnet-aec1d4d9
    ParameterKey=bigipExternalSecurityGroup,ParameterValue=sg-d90eb9be
    ParameterKey=webserverPrivateIp,ParameterValue="10.0.3.8"
    ParameterKey=bigip1LicenseKey,ParameterValue=NEHQF-CDKUY-RJTJB-XSPTZ-XVKSQJS


####Existing Stack - BYOL w/ WAF:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://existing-stack-byol-1nic-bigip-w-waf.template
    --stack-name existing-stack-bigip-1nic-w-waf
    --parameters  
    ParameterKey=sshKey,ParameterValue=YOUR-SSH-KEY
    ParameterKey=bigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=bigipPerformanceType,ParameterValue=Best
    ParameterKey=bigipAdminUsername,ParameterValue=admin
    ParameterKey=bigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=bigipManagementGuiPort,ParameterValue=443
    ParameterKey=vpc,ParameterValue=vpc-61a94705
    ParameterKey=az1ExternalSubnet,ParameterValue=subnet-aec1d4d9
    ParameterKey=bigipExternalSecurityGroup,ParameterValue=sg-d90eb9be
    ParameterKey=webserverPrivateIp,ParameterValue="10.0.3.8"
    ParameterKey=bigip1LicenseKey,ParameterValue=NEHQF-CDKUY-RJTJB-XSPTZ-XZKSQIS

_NOTE:_ _The only difference for "with WAF" example above is the template name and "Performance Type" = Best_

####Existing Stack - BIG-IQ License Pool:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://existing-stack-bigiq-license-pool-1nic-bigip.template
    --stack-name existing-stack-bigiq-license-pool-bigip-1nic
    --parameters  
    ParameterKey=sshKey,ParameterValue=YOUR-SSH-KEY
    ParameterKey=bigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=bigipPerformanceType,ParameterValue=Good
    ParameterKey=bigipAdminUsername,ParameterValue=admin
    ParameterKey=bigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=bigipManagementGuiPort,ParameterValue=443
    ParameterKey=vpc,ParameterValue=vpc-61a94705
    ParameterKey=az1ExternalSubnet,ParameterValue=subnet-aec1d4d9
    ParameterKey=bigipExternalSecurityGroup,ParameterValue=sg-d90eb9be
    ParameterKey=webserverPrivateIp,ParameterValue="10.0.3.8"
    ParameterKey=bigiqUsername,ParameterValue=admin 
    ParameterKey=bigiqPassword,ParameterValue='YOURPASSWORD' 
    ParameterKey=bigiqAddress,ParameterValue=52.89.223.222 
    ParameterKey=bigiqLicensePoolUUID,ParameterValue=5ba3f9b1-52f1-4fd1-93fd-111111b5aa23


###2 NIC:

####Full Stack:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://full-stack-vpc-w-byol-2nic-bigip.template 
    --stack-name full-stack-bigip-2nic
    --parameters  
    ParameterKey=sshKey,ParameterValue=YOUR-SSH-KEY
    ParameterKey=availabilityZone1,ParameterValue=us-west-2a
    ParameterKey=availabilityZone2,ParameterValue=us-west-2b
    ParameterKey=bigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=bigipPerformanceType,ParameterValue=Good
    ParameterKey=webserverInstanceType,ParameterValue=t1.micro
    ParameterKey=bigipAdminUsername,ParameterValue=admin
    ParameterKey=bigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=bigip1LicenseKey,ParameterValue=HOXXC-QTDPU-KARFZ-GCNAN-EKVPEDU

####Existing Stack:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://existing-stack-byol-2nic-bigip.template
    --stack-name existing-stack-bigip-2nic
    --parameters  
    ParameterKey=sshKey,ParameterValue=YOUR-SSH-KEY
    ParameterKey=bigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=bigipPerformanceType,ParameterValue=Good
    ParameterKey=bigipAdminUsername,ParameterValue=admin
    ParameterKey=bigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=vpc,ParameterValue=vpc-8a05ebee
    ParameterKey=az1ExternalSubnet,ParameterValue=subnet-436d7934
    ParameterKey=az1ManagementSubnet,ParameterValue=subnet-406d7937
    ParameterKey=bigipExternalSecurityGroup,ParameterValue=sg-bd8c3dda
    ParameterKey=bigipManagementSecurityGroup,ParameterValue=sg-bc8c3ddb
    ParameterKey=webserverPrivateIp,ParameterValue="10.0.3.39"
    ParameterKey=bigip1LicenseKey,ParameterValue=CCSVQ-ZXHDA-JBJYU-ZKXZI-LLUHUMX


## deploy_stacks.py

As a further convience, we have included a simple python script ( deploy/deploy_stacks.py ) that can string together the two related tempates. 

Reqirements:

boto3

For more information, see:
https://github.com/boto/boto3

ex.

    python deploy_stacks.py -t full-stack-vpc-w-byol-1nic-bigip.template,existing-stack-byol-1nic-bigip.template -r TEQNR-OUBKH-YGRLC-ISTMV-WCBNYGN,WRZUG-PSFAF-DFRBR-AXAIP-GEZDDTC

    or:
    python deploy_stacks.py -t full-stack-bigiq-license-pool-1nic-bigip-w-waf.template,existing-stack-bigiq-license-pool-1nic-bigip-w-waf.template

This will launch the first full stack (vpc, subnets, security groups, webserver and Big-IP) and use the various outputs (vpc, subnets, security groups, etc.) for creating the next stack (Big-IP in an existing stack).  

ex.

    python deploy_stacks.py -t infra-only-for-2nic-bigip.template,existing-stack-byol-2nic-bigip.template -r ,HJQMG-QDEPB-BEIMO-XDGJB-JZWNOYU

Above will launch the first infra-only stack (vpc, subnets, security groups, webserver) and use the various outputs (vpc, subnets, security groups, etc.) for creating the next stack (Big-IP in an existing stack). Note, the first template does not have a Big-IP but number of comma seperated entries provided for reg_keys parameter must match number and order of templates provided so templates with Big-IPs will get associated keys passed. 



## Troubleshooting steps

This section provides steps intended to assist with troubleshooting common problems with AWS CloudFormation deployments: 

  - In a case of stack creation failures, disabling rollback allows to preview events for each provisioned resource as well as preview cf-init.log; see [AWS Docs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-init.html#cfn-init-Examples) for more details
  - There are several common reasons for deployment failure: 
    * Missing pre-request; see "Prerequisites" section for a particular AWS CloudFomration Template; see [example](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/supported/standalone/1nic/existing-stack/payg/README.md#prerequisites) for more details
    * Missing required parameters; see "Template parameters" section for the complete list of template paramteres required for a particular AWS CloudFormation Template; see [example](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/supported/standalone/1nic/existing-stack/payg/README.md#user-content-installing-the-image-using-the-aws-launch-stack-button) for more details 
    * Missing required resources/infastruture; extistent stack templates require existent infastructure
    * Lack of permissions for IAM user used for CloudFormation deployment
    * Template validation problem; using the [validate-template](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/validate-template.html) method allows to validate template against AWS
  - AWS Docs provide additional details on possible resolutions of common AWS problems [AWS Docs Troubleshooing](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/troubleshooting.html#troubleshooting-errors)
  - In case of recieving deployment failure during BIGIP on-boarding, the BIGIP service logs allow to get insights about the problem: 
    * /var/log/restnoded/restnoded.log - [AS3](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/about-as3.html) error log
    * /var/log/restjavad.[0-9].log - restjavad logs; this service provides control-plane access to the BIG-IP using an http REST api.
    * /var/log/cloud/aws/ - this directory includes logs generated by [f5-cloud-libs](https://github.com/F5Networks/f5-cloud-libs) tool intended for on-boarding and configuring BIGIP device; the following page [f5-cloud-libs](https://github.com/F5Networks/f5-cloud-libs/blob/master/USAGE.md) provides details about each module used by f5-cloud-libs


## Known Issues:


1. Some Full stack templates may get too large to be deployed via AWS cli.

        'templateBody' failed to satisfy constraint: Member must have length less than or equal to 51200

   **Workaround:** _Use AWS console, store template on S3, or minify_




