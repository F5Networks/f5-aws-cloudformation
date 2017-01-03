# Deploying the BIG-IP in AWS - Single NIC

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction
This solution uses a CloudFormation Template to launch a single NIC deployment a BIG-IP VE in an Amazon Virtual Private Cloud. Traffic flows from the BIG-IP VE to the application servers.  This is the standard Cloud design where the compute instance of
F5 is running with a single interface, which processes both management and data plane traffic.  This is a traditional model in the cloud where the deployment is considered one-armed.

This solution provides two different template options:
  - **BYOL**<br>
  The BYOL (bring your own license) template allows you to input an existing BIG-IP license.
  - **Hourly**<br>
  The Hourly template which uses pay-as-you-go hourly billing
  
  The **existing stack** CloudFormation template incorporates an existing Virtual Private Cloud (VPC). If you would like to run a *full stack* which creates and configures the BIG-IP, the AWS infrastructure, as well as a backend webserver, see the templates located in the **learning-stacks** folder.
  
  See the [Configuration Example](#config) section for a configuration diagram and more information for this solution.
  
## Prerequisites
The following are prerequisites for the F5 single NIC CFT:
  - An AWS VPC with one subnet
  - An AWS security group that allows port 22 for SSH access to BIG-IP VE
  - The AWS security group should include the GUI port you specify in the CFT (8443 by default) for BIG-IP access. It should also include any port required to access your application virtual server.
  - Key pair for SSH access to BIG-IP VE (you can create or import in AWS)

## Supported instance types and hypervisors
  - For a list of supported AWS instance types for this solutions, see the **Amazon EC2 instances for BIG-IP VE** section of https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-amazon-ec2-12-1-0/1.html

  - For a list versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and AWS, see https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html.


## Installation

You have two options for deploying this template: 
  - Using the AWS deploy buttons 
  - Using [CLI Tools](#cli)

### Using the AWS deploy buttons
The easiest way to deploy of the of CloudFormation templates is to use the appropriate Launch button.
 - Hourly
 - [BYOL](#byol)
<br><br>

**Hourly deploy button**

Use this button to deploy the **hourly** template: 

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-1nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/>
</a>
<br>
<br>

**Hourly Parameters**
After clicking the Launch button, you must specify the following parameters.


| Parameter | Required | Description |
| --- | --- | --- |
| adminPassword | x | Type the BIG-IP admin password |
| adminUsername | x | Type the BIG_IP user name |
| bigipExternalSecurityGroup | x | Public or External Security Group ID |
| imageName | x | F5 BIG-IP Performance Type |
| instanceType | x | BIG-IP virtual instance type |
| managementGuiPort | x | Port to use for the management port GUI |
| restrictedSrcAddress | x | The IP address range that can be used to SSH to the EC2 instances |
| sshKey | x | Name of an existing EC2 KeyPair to enable SSH acccess to the instance |
| subnet1Az1 | x | Public or External subnet ID |
| Vpc | x | Common VPC for the deployment |

<br>
<a name="byol"></a>**BYOL deploy button**

Use this button to deploy the **BYOL** template: 

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-1nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/>
</a>

<br>
<br>
**BYOL Parameters**
After clicking the Launch button, you must specify the following parameters.

| Parameter | Required | Description |
| --- | --- | --- |
| adminPassword | x | Type the BIG-IP admin password |
| adminUsername | x | Type the BIG-IP user name |
| bigipExternalSecurityGroup | x | Public or External Security Group ID |
| imageName | x | F5 BIG-IP Performance Type |
| instanceType | x | BIG-IP virtual instance type |
| licenseKey1 | x | Type or paste your F5 BYOL regkey here |
| managementGuiPort | x | Port to use for the management port GUI |
| restrictedSrcAddress | x | The IP address range that can be used to SSH to the EC2 instances |
| sshKey | x | Name of an existing EC2 KeyPair to enable SSH acccess to the instance |
| subnet1Az1 | x | Public or External subnet ID |
| Vpc | x | Common VPC for the deployment |


### <a name="cli"></a>AWS CLI Usage
Coming soon

## Configuration Example <a name="config">

The following is a simple configuration diagram for this single NIC deployment. In this scenario, all access to the BIG-IP VE appliance is through the same IP address and virtual network interface (vNIC).  This interface processes both management and data plane traffic.

![Single NIC configuration example](images/AWS-1nic.png)
### Documentation
The ***BIG-IP Virtual Edition and Amazon Web Services: Single NIC Setup*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-amazon-ec2-12-1-0.html) details how to create the configuration manually without using the CloudFormation template.  This document also decribes the configuration in more detail.

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
