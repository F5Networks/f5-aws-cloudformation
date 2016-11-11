# Autoscaling the BIG-IP Web Application Firewall in AWS
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Doc Status](http://readthedocs.org/projects/f5-sdk/badge/?version=latest)](https://f5.com/solutions/deployment-guides)

## Introduction
This project implements auto scaling of BIG-IP Web Application Firewall (WAF) systems in Amazon Web Services using the AWS CloudFormation template **autoscale-bigip.template**. As traffic increases or decreases, the number of BIG-IP instances automatically increases or decreases accordingly.

## Documentation
See the project documentation on (TBD).

## BIG-IP deployment and configuration

All BIG-IPs are deployed with a single interface attached to a public subnet. Advanced traffic management functionality is provided through use of BIG-IP Local Traffic Manager (LTM) and Application Security Manager (ASM). The default **Best 25Mbs** image available in the AWS marketplace is used to license these modules.
All of the BIG-IP configuration is performed at device bootup using `CloudInit`. This can be seen in autoscale-bigip.template CloudFormation template. In general, CloudInit is used to :

- Set the BIG-IP hostname, NTP, and DNS settings
- Configure an IAM (Identity and Access Management) role with policies allowing the BIG-IP to make authenticated calls to AWS HTTPS endpoints.
- Create an HTTP virtual server with a Web Application Firewall policy
- Deploy integration with EC2 Autoscale and CloudWatch services for scaling of the BIG-IP tier.


### Installation ###
Download the CloudFormation template from https://github.com/f5networks and use it to create a stack in AWS Cloudformation either using the AWS Console or AWS CLI

**AWS Console**

 From the AWS Console main page: 
   1. Under AWS Services, click **CloudFormation**.
   2. Click the **Create Stack** button 
   3. In the Choose a template area, click **Upload a template to Amazon S3**.
   4. Click **Choose File** and then browse to the **autoscale-bigip.template** file.
 
 
 **AWS CLI**
 
 From the AWS CLI, use the following command syntax:
 ```
 aws cloudformation create-stack --stack-name my-autoscale-bigip --template-body file:///fullfilepath/autoscale-bigip.template --parameters file:///fullfilepath/autoscale-bigip-parameters.json --capabilities CAPABILITY_NAMED_IAM
```

### Usage ###
Use this template to automate the autoscale implementation by providing the parameter values. You can use or change the default parameter values, which are defined in the AWS CloudFormation template on the AWS Console.  If using the AWS CLI, use the following JSON format parameter file


| Parameter | Required | Description |
| --- | --- | --- |
| deploymentName | x | Deployment Name - Used in creating objects |
| vpc | x | Common VPC for whole deployment |
| availabilityZones | x | Availability zones in which BIG-IP is being deployed |
| subnets | x | AZ Public or External Subnet IDs |
| bigipSecurityGroup | x | Pre-existing security group for BIG-IP |
| bigipElasticLoadBalancer | x | Elastic Load Balancer group for all BIG-IPs. "Default": "BigipElasticLoadBalancer" |
| keyName | x | Name of an existing EC2 KeyPair to enable SSH access to the instance |
| sshLocation | x | The IP address range that can be used to SSH to the EC2 instances |
| instanceType | x | F5 BIG-IP Instance Type. "Default": "m4.2xlarge" |
| performanceType | x | F5 BIG-IP Performance Type. "Default": "Best" |
| throughput | x | F5 BIG-IP Throughput. "Default": "25-Mbps" |
| adminPassword | x | Please enter your BIG-IP Admin Password |
| managementGuiPort | x | Port to use for the managment GUI. "Default": 443 |
| timezone | x | Enter a Olson timezone string from /usr/share/zoneinfo. "Default": "UTC" |
| ntpServers | x | Enter a space list of NTP servers. ex. 0.pool.ntp.org 1.pool.ntp.org. "Default": "0.pool.ntp.org" |
| scalingMinSize | x | Enter the minimum number of BIG-IP instances (1-8) to be available in the AutoScale Group. "Default": "1" |
| scalingMaxSize | x | Enter the maximum number of BIG-IP instances (2-8) that can be created in the AutoScale Group. "Default": "3" |
| scaleDownBytesThreshold | x | Enter bytes to begin Scaling Down. "Default": "10000" |
| scaleUpBytesThreshold | x | Enter bytes to begin Scaling Up. "Default": "35000" |
| notificationEmail |  | Enter a valid email address to send AutoScaling Event Notifications |
| virtualServicePort | x | The port for the Virtual Service on the Big-IP |
| applicationPort | x | The Pool Member Port. "Default": "80" |
| appInternalElbDnsName | x | DNS of the ELB used for the application. "Default": "XXXXXXX.region.elb.amazonaws.com" |





Example **autoscale-bigip-parameters.json**
```
[
	{
		"ParameterKey":"vpc",
		"ParameterValue":"vpc-1ffef478"
	},
	{
		"ParameterKey":"availabilityZones",
		"ParameterValue":"us-east-1a,us-east-1b,us-east-1c"
	},
	{
		"ParameterKey":"subnets",
		"ParameterValue":"subnet-88d30fa5,subnet-2dc44b64,subnet-413cec1a"
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
		"ParameterValue":"awskeypair-east"
	},
	{
		"ParameterKey":"keyName",
		"ParameterValue":"awskeypair-east"
	},
	{
		"ParameterKey":"keyName",
		"ParameterValue":"awskeypair-east"
	},
	{
		"ParameterKey":"keyName",
		"ParameterValue":"awskeypair-east"
	},
	{
		"ParameterKey":"adminPassword",
		"ParameterValue":"GoF5!"
	},
		"ParameterKey":"notificationEmail",
		"ParameterValue":"k.koh@f5.com"
	},

	{
		ParameterKey:"appInternalElbDnsName",
		ParameterValue:"internal-A1-AppElb-911355308.us-east-1.elb.amazonaws.com"
	}
]
```