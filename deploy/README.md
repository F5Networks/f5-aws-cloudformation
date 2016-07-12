
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
[full-stack-hourly-1nic-bigip.template](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/unsupported/full-stack-byol-1nic-bigip.template)


If you are familiar with AWS and have an existing stack, we recommend first trying:

[existing-stack-hourly-1nic-bigip.template](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/unsupported/existing-stack-hourly-1nic-bigip.template)

and taking a look at:

[security-groups-for-1nic-bigip.template](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/unsupported/security-groups-for-1nic-bigip.template)

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
    --template-body file://full-stack-vpc-w-byol-1nic-bigip.template 
    --stack-name full-stack-bigip-1nic
    --parameters  
    ParameterKey=KeyName,ParameterValue=YOUR-SSH-KEY
    ParameterKey=AvailabilityZone1,ParameterValue=us-west-2a
    ParameterKey=AvailabilityZone2,ParameterValue=us-west-2b
    ParameterKey=BigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=BigipPerformanceType,ParameterValue=Good
    ParameterKey=WebserverInstanceType,ParameterValue=t1.micro
    ParameterKey=BigipAdminUsername,ParameterValue=admin
    ParameterKey=BigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=BigipManagementGuiPort,ParameterValue=443
    ParameterKey=Bigip1LicenseKey,ParameterValue=LUFJD-YREAG-VQHVI-EYOQH-JBBKXAI

####Existing Stack - BYOL:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://existing-stack-byol-1nic-bigip.template
    --stack-name existing-stack-bigip-1nic
    --parameters  
    ParameterKey=KeyName,ParameterValue=YOUR-SSH-KEY
    ParameterKey=BigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=BigipPerformanceType,ParameterValue=Good
    ParameterKey=BigipAdminUsername,ParameterValue=admin
    ParameterKey=BigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=BigipManagementGuiPort,ParameterValue=443
    ParameterKey=Vpc,ParameterValue=vpc-61a94705
    ParameterKey=Az1ExternalSubnet,ParameterValue=subnet-aec1d4d9
    ParameterKey=BigipExternalSecurityGroup,ParameterValue=sg-d90eb9be
    ParameterKey=WebserverPrivateIp,ParameterValue="10.0.3.8"
    ParameterKey=Bigip1LicenseKey,ParameterValue=NEHQF-CDKUY-RJTJB-XSPTZ-XVKSQJS


####Existing Stack - BYOL w/ WAF:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://existing-stack-byol-1nic-bigip-w-waf.template
    --stack-name existing-stack-bigip-1nic-w-waf
    --parameters  
    ParameterKey=KeyName,ParameterValue=YOUR-SSH-KEY
    ParameterKey=BigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=BigipPerformanceType,ParameterValue=Best
    ParameterKey=BigipAdminUsername,ParameterValue=admin
    ParameterKey=BigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=BigipManagementGuiPort,ParameterValue=443
    ParameterKey=Vpc,ParameterValue=vpc-61a94705
    ParameterKey=Az1ExternalSubnet,ParameterValue=subnet-aec1d4d9
    ParameterKey=BigipExternalSecurityGroup,ParameterValue=sg-d90eb9be
    ParameterKey=WebserverPrivateIp,ParameterValue="10.0.3.8"
    ParameterKey=Bigip1LicenseKey,ParameterValue=NEHQF-CDKUY-RJTJB-XSPTZ-XZKSQIS

_NOTE:_ _The only difference for "with WAF" example above is the template name and "Performance Type" = Best_

####Existing Stack - BIG-IQ License Pool:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://existing-stack-bigiq-license-pool-1nic-bigip.template
    --stack-name existing-stack-bigiq-license-pool-bigip-1nic
    --parameters  
    ParameterKey=KeyName,ParameterValue=YOUR-SSH-KEY
    ParameterKey=BigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=BigipPerformanceType,ParameterValue=Good
    ParameterKey=BigipAdminUsername,ParameterValue=admin
    ParameterKey=BigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=BigipManagementGuiPort,ParameterValue=443
    ParameterKey=Vpc,ParameterValue=vpc-61a94705
    ParameterKey=Az1ExternalSubnet,ParameterValue=subnet-aec1d4d9
    ParameterKey=BigipExternalSecurityGroup,ParameterValue=sg-d90eb9be
    ParameterKey=WebserverPrivateIp,ParameterValue="10.0.3.8"
    ParameterKey=BigiqUsername,ParameterValue=admin 
    ParameterKey=BigiqPassword,ParameterValue='YOURPASSWORD' 
    ParameterKey=BigiqAddress,ParameterValue=52.89.223.222 
    ParameterKey=BigiqLicensePoolUUID,ParameterValue=5ba3f9b1-52f1-4fd1-93fd-111111b5aa23


###2 NIC:

####Full Stack:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://full-stack-vpc-w-byol-2nic-bigip.template 
    --stack-name full-stack-bigip-2nic
    --parameters  
    ParameterKey=KeyName,ParameterValue=YOUR-SSH-KEY
    ParameterKey=AvailabilityZone1,ParameterValue=us-west-2a
    ParameterKey=AvailabilityZone2,ParameterValue=us-west-2b
    ParameterKey=BigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=BigipPerformanceType,ParameterValue=Good
    ParameterKey=WebserverInstanceType,ParameterValue=t1.micro
    ParameterKey=BigipAdminUsername,ParameterValue=admin
    ParameterKey=BigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=Bigip1LicenseKey,ParameterValue=HOXXC-QTDPU-KARFZ-GCNAN-EKVPEDU

####Existing Stack:

    aws cloudformation create-stack 
    --region us-west-2 
    --template-body file://existing-stack-byol-2nic-bigip.template
    --stack-name existing-stack-bigip-2nic
    --parameters  
    ParameterKey=KeyName,ParameterValue=YOUR-SSH-KEY
    ParameterKey=BigipInstanceType,ParameterValue=m3.xlarge
    ParameterKey=BigipPerformanceType,ParameterValue=Good
    ParameterKey=BigipAdminUsername,ParameterValue=admin
    ParameterKey=BigipAdminPassword,ParameterValue='YOURPASSWORD'
    ParameterKey=Vpc,ParameterValue=vpc-8a05ebee
    ParameterKey=Az1ExternalSubnet,ParameterValue=subnet-436d7934
    ParameterKey=Az1ManagementSubnet,ParameterValue=subnet-406d7937
    ParameterKey=BigipExternalSecurityGroup,ParameterValue=sg-bd8c3dda
    ParameterKey=BigipManagementSecurityGroup,ParameterValue=sg-bc8c3ddb
    ParameterKey=WebserverPrivateIp,ParameterValue="10.0.3.39"
    ParameterKey=Bigip1LicenseKey,ParameterValue=CCSVQ-ZXHDA-JBJYU-ZKXZI-LLUHUMX


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



#####Known Issues:


1. Some Full stack templates may get too large to be deployed via AWS cli.

        'templateBody' failed to satisfy constraint: Member must have length less than or equal to 51200

   **Workaround:** _Use AWS console, store template on S3, or minify_




