# Auto scaling the BIG-IP VE Web Application Firewall in AWS
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Doc Status](http://readthedocs.org/projects/f5-sdk/badge/?version=latest)](https://f5.com/solutions/deployment-guides)

## Introduction
This project implements auto scaling of BIG-IP Virtual Edition Web Application Firewall (WAF) systems in Amazon Web Services using the AWS CloudFormation template **autoscale-bigip.template**. As traffic increases or decreases, the number of BIG-IP VE instances automatically increases or decreases accordingly.

## Documentation
The ***BIG-IP Virtual Edition and Amazon Web Services: Auto Scaling*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-autoscaling-amazon-ec2-12-1-0.html) decribes how to create the configuration manually without using the CloudFormation template.

## BIG-IP deployment and configuration

All BIG-IP VE instances deploy with a single interface (NIC) attached to a public subnet. This single interface processes both management and data plane traffic.  The <a href="https://f5.com/products/big-ip/local-traffic-manager-ltm">BIG-IP Local Traffic Manager</a> (LTM) and <a href="https://f5.com/products/big-ip/application-security-manager-asm">Application Security Manager</a> (ASM) provide advanced traffic management and security functionality. The CloudFormation template uses the default **Best 1000Mbs** image available in the AWS marketplace to license these modules.
The template performs all of the BIG-IP VE configuration when the device boots using `Cloud-Init`. In general, Cloud-Init is used to:

- Set the BIG-IP hostname, NTP, and DNS settings
- Configure an IAM (Identity and Access Management) role with policies allowing the BIG-IP to make authenticated calls to AWS HTTPS endpoints.
- Create a HTTP virtual server with a Web Application Firewall policy
- Deploy integration with EC2 Autoscale and CloudWatch services for scaling of the BIG-IP tier.


### Installation
Download the CloudFormation template from https://github.com/f5networks and use it to create a stack in AWS CloudFormation either using the AWS Console or AWS CLI

**AWS Console**

 From the AWS Console main page: 
   1. Under AWS Services, click **CloudFormation**.
   2. Click the **Create Stack** button 
   3. In the Choose a template area, click **Upload a template to Amazon S3**.
   4. Click **Choose File** and then browse to the **autoscale-bigip.template** file.
 
 <br>
 **AWS CLI**
 
 From the AWS CLI, use the following command syntax:
 ```
 aws cloudformation create-stack --stack-name A1-autoscale-bigip --template-body file:///fullfilepath/autoscale-bigip.template --parameters file:///fullfilepath/autoscale-bigip-parameters.json --capabilities CAPABILITY_NAMED_IAM`
```
<br>
### Usage ###
Use this template to automate the autoscale implementation by providing the parameter values. You can use or change the default parameter values, which are defined in the AWS CloudFormation template on the AWS Console.  If using the AWS CLI, use the following JSON format parameter file


| Parameter | Required | Description |
| --- | --- | --- |
| deploymentName | x | Deployment Name - Used in creating objects |
| vpc | x | Common VPC for whole deployment |
| availabilityZones | x | Availability zones in which BIG-IP is being deployed |
| subnets | x | AZ Public or External Subnet IDs |
| bigipSecurityGroup | x | Pre-existing security group for BIG-IP |
| bigipElasticLoadBalancer | x | Elastic Load Balancer group for all BIG-IPs. "Default": "enterBigipElasticLoadBalancerName" |
| keyName | x | Name of an existing EC2 KeyPair to enable SSH access to the instance |
| sshLocation | x | The IP address range that can be used to SSH to the EC2 instances |
| instanceType | x | F5 BIG-IP Instance Type. "Default": "m3.2xlarge" |
| performanceType | x | F5 BIG-IP Performance Type. "Default": "Best" |
| throughput | x | F5 BIG-IP Throughput. "Default": "25-Mbps" |
| adminPassword | x | Please enter your BIG-IP Admin Password |
| managementGuiPort | x | Port to use for the managment GUI. "Default": 8443 |
| timezone | x | Enter a Olson timezone string from /usr/share/zoneinfo. "Default": "UTC" |
| ntpServer | x | Enter a NTP server. "Default": "0.pool.ntp.org" |
| scalingMinSize | x | Enter the minimum number of BIG-IP instances (1-8) to be available in the AutoScale Group. "Default": "1" |
| scalingMaxSize | x | Enter the maximum number of BIG-IP instances (2-8) that can be created in the AutoScale Group. "Default": "3" |
| scaleDownBytesThreshold | x | Enter bytes to begin Scaling Down. "Default": "10000" |
| scaleUpBytesThreshold | x | Enter bytes to begin Scaling Up. "Default": "35000" |
| notificationEmail |  | Enter a valid email address to send AutoScaling Event Notifications |
| virtualServicePort | x | The port for the Virtual Service on the BIG-IP. "Default": 80 |
| applicationPort | x | The Pool Member Port. "Default": "80" |
| appInternalElbDnsName | x | DNS of the ELB used for the application. "Default": "XXXXXXX.region.elb.amazonaws.com" as example to user |
| policyLevel | x | WAF Policy Level. "Default": "high" |
<br>




Example minimum **autoscale-bigip-parameters.json** using default values for unlisted parameters
```json
[
	{
		"ParameterKey":"vpc",
		"ParameterValue":"vpc-1ffef478"
	},
	{
		"ParameterKey":"availabilityZones",
		"ParameterValue":"us-east-1a,us-east-1b"
	},
	{
		"ParameterKey":"subnets",
		"ParameterValue":"subnet-88d30fa5,subnet-2dc44b64"
	},
	{
		"ParameterKey":"bigipSecurityGroup",
		"ParameterValue":"sg-13ee026e"
	},
	{
		"ParameterKey":bigipElasticLoadBalancer,
		"ParameterValue":"A1-BigipElb"
	},
	{
		"ParameterKey":"keyName",
		"ParameterValue":"awskeypair"
	},
	{
		"ParameterKey":"sshLocation",
		"ParameterValue":"0.0.0.0/0"
	},
	{
		"ParameterKey":"adminPassword",
		"ParameterValue":"strongPassword"
	},
		"ParameterKey":"notificationEmail",
		"ParameterValue":"user@company.com"
	},
	{
		ParameterKey:"appInternalElbDnsName",
		ParameterValue:"internal-A1-AppElb-911355308.us-east-1.elb.amazonaws.com"
	},
	{
		ParameterKey:"policyLevel",
		ParameterValue:"high"
	}
]
```