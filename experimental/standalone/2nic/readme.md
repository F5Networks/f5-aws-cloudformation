# Deploying the BIG-IP in AWS - 2 NIC

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction

This solution uses a Cloud Formation Template to launch a 2-NIC deployment of a BIG-IP VE in an Amazon Virtual Private Cloud. In a 2-NIC implementation, one interface is for management and data-plane traffic from the Internet, and the second interface is connected into the Amazon networks where traffic is processed by the pool members in a traditional two-ARM design. Traffic flows from the BIG-IP VE to the application servers.

This solution provides two different template options:
  - **BYOL**<br>
  The BYOL (bring your own license) template allows you to input an existing BIG-IP license.
  - **Hourly**<br>
  The Hourly template which uses pay-as-you-go hourly billing
  
  The **existing stack** CloudFormation template incorporates an existing Virtual Private Cloud (VPC). If you would like to run a *full stack* which creates and configures the BIG-IP, the AWS infrastructure, as well as a backend webserver, see the templates located in the **learning-stacks** folder.

## Prerequisites
The following are prerequisites for the F5 2-NIC CFT:
  - An AWS VPC with three subnets: 
    - Management subnet (called Public in the AWS UI)
    - External subnet (called Private in the AWS UI) 
    - NAT instance and associated network interface for network translation.
  - An AWS security group that allows port 22 for SSH access to BIG-IP VE
  - The AWS security group should include the GUI port you specify in the CFT (8443 by default) for BIG-IP access. It should also include any port required to access your application virtual server.
  - Key pair for SSH access to BIG-IP VE (you can create or import in AWS)

## Supported instance types and hypervisors
  - For a list of supported AWS instance types for this solutions, see the **Amazon EC2 instances for BIG-IP VE** section of https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-multi-nic-setup-amazon-ec2-12-1-0/1.html#guid-71265d82-3a1a-43d2-bae5-892c184cc59b

  - For a list versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and AWS, see https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html.

<<<<<<< HEAD
=======
### Help
We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 CloudFormation templates.  This channel is typically monitored Monday-Friday 9-5 PST by F5 employees who will offer best-effort support.<br>
While this template has been created by F5 Networks, it is in the experimental directory and therefore has not completed full testing and is subject to change.  F5 Networks does not offer technical support for templates in the experimental directory. For supported templates, see the templates in the **supported** directory.

>>>>>>> develop
## Installation

You have two options for deploying this template: 
  - Using the AWS deploy buttons 
  - Using [CLI Tools](#cli)

### Using the AWS deploy buttons
<<<<<<< HEAD
The easiest way to deploy of the of CloudFormation templates is to use the appropriate Launch button.
<br>
=======
The easiest way to deploy one of the CloudFormation templates is to use the appropriate Launch button.
 - Hourly, which uses pay-as-you-go hourly billing
 - [BYOL](#byol) (bring your own license), which allows you to use an existing BIG-IP license.
>>>>>>> develop
<br>

**Hourly deploy button**

Use this button to deploy the **hourly** template: 

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/>
</a>
<br>
<br>

After clicking the Launch button, you must specify the following parameters.
<br>

| Parameter | Required | Description |
| --- | --- | --- |
| adminPassword | x | Type the BIG-IP admin password |
| adminUsername | x | Type the BIG_IP user name |
| bigipExternalSecurityGroup | x | Public or External Security Group ID |
| bigipManagementSecurityGroup | x | BIG-IP Management Security Group ID |
| imageName | x | F5 BIG-IP Performance Type |
| instanceType | x | BIG-IP virtual instance type |
| licenseKey1 | x | Type or paste your F5 BYOL regkey |
| managementSubnetAz1 | x | Management subnet ID |
| restrictedSrcAddress | x | The IP address range that can be used to SSH to the EC2 instances |
| sshKey | x | Name of an existing EC2 KeyPair to enable SSH acccess to the instance |
| subnet1Az1 | x | Public or External subnet ID |
| Vpc | x | Common VPC for the deployment |

<br>
<br>

  **BYOL deploy button**

Use this button to deploy the **BYOL** template: 

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/>
</a>
<br>
After clicking the Launch button, you must specify the following parameters.

| Parameter | Required | Description |
| --- | --- | --- |
| adminPassword | x | Type the BIG-IP admin password |
| adminUsername | x | Type the BIG_IP user name |
| bigipExternalSecurityGroup | x | Public or External Security Group ID |
| bigipManagementSecurityGroup | x | BIG-IP Management Security Group ID |
| iamAccessKey | x | Type the IAM Access Key |
| iamSecretKey | x | Type the IAM Secret Key for BIG-IP |
| imageName | x | F5 BIG-IP Performance Type |
| instanceType | x | BIG-IP virtual instance type |
| licenseKey1 | x | Type or paste your F5 BYOL regkey here |
| licenseKey2 | x | Type or paste your F5 BYOL regkey here |
| managementSubnetAz1 | x | Management subnet ID |
| managementSubnetAz2 | x | Management subnet ID |
| restrictedSrcAddress | x | The IP address range that can be used to SSH to the EC2 instances |
| sshKey | x | Name of an existing EC2 KeyPair to enable SSH acccess to the instance |
| subnet1Az1 | x | Public or External subnet ID |
| subnet1Az2 | x | Public or External subnet ID |
| Vpc | x | Common VPC for the deployment |


### <a name="cli"></a>AWS CLI Usage
Coming soon

## Configuration Example <a name="config">

The following is a simple configuration diagram for this 2-NIC deployment. In this diagram, the IP addresses are provided as examples.
![2-NIC configuration example](images/aws-1nic.png)

### Documentation
The ***BIG-IP Virtual Edition and Amazon Web Services: Multi-NIC Setup*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-multi-nic-setup-amazon-ec2-12-1-0.html) details how to create the configuration manually without using the CloudFormation template.  This document also describes the configuration in more detail.

## Design Patterns


The goal is for the design patterns for all the iterative examples of F5 being deployed via ARM templates to closely match as much as possible.

### List of Patterns For Contributing Developers


 1. Still working on patterns to use

## Filing Issues

See the Issues section of `Contributing <CONTRIBUTING.md>`__.

## Contributing

See `Contributing <CONTRIBUTING.md>`__

## Test


Before you open a pull request, your code must have passed a deployment into Azure with the intended result



## Copyright

Copyright 2014-2016 F5 Networks Inc.


## License


Apache V2.0
~~~~~~~~~~~
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Individuals or business entities who contribute to this project must have
completed and submitted the `F5 Contributor License Agreement`