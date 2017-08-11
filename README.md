# F5 AWS CloudFormation templates
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-aws-cloudformation.svg)](https://github.com/f5networks/f5-aws-cloudformation/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-aws-cloudformation.svg)](https://github.com/f5networks/f5-aws-cloudformation/issues)

## Introduction
 
Welcome to the GitHub repository for F5's CloudFormation templates for deploying F5 in Amazon Web Services.  All of the templates in this repository have been developed by F5 Networks engineers. Across all branches in this repository, there are two directories: *supported* and *experimental*

  - **supported**<br>
  The *supported* directory contains CloudFormation templates that have been created and fully tested by F5 Networks. These templates are fully supported by F5, meaning you can get assistance if necessary from F5 Technical Support via your typical methods.

  - **experimental**<br>
  The *experimental* directory also contains CloudFormation templates that have been created by F5 Networks. However, these templates have not completed full testing and are subject to change. F5 Networks does not offer technical support for templates in the experimental directory, so use these templates with caution.

## Template information
Descriptions for each template are contained at the top of each template in the *Description* key.
For additional information, including how the templates are generated, and assistance in deploying a template, see the README file on the individual template pages.


## List of Supported F5 CloudFormation templates for AWS deployments
The following is a list of the current *supported* F5 CloudFormation templates. Click the links below to view the README files which include the Launch buttons, or click the **Launch Stack** buttons to immediately launch the stack. Because individual templates may have specific prerequisites, we strongly recommend you view the README file before attempting to launch a template. 

**Important**: You may have to select the AWS region in which you want to deploy after clicking the Launch Stack button
<br><br>
<a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/1nic">**Standalone BIG-IP VE - Single NIC**</a>
  - Hourly<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-1nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a><br>
    
  - BYOL<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-1nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
    
  - Using BIG-IQ for Licensing<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-bigiq-1nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a> 

<a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/2nic">**Standalone BIG-IP VE - 2 NICs**</a>
  - Hourly<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a><br>

  - BYOL<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
    
  - Using BIG-IQ for Licensing<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-bigiq-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a> 

<a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/3nic">**Standalone BIG-IP VE - 3 NICs**</a>
  - Hourly<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-3nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a><br>

  - BYOL<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-3nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
  
  - Using BIG-IQ for Licensing<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-bigiq-3nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a> 

**Clustered BIG-IP VE - 2 NICs**
  - <a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/cluster/2nic/same-az-ha">Same Availability Zone</a>
    - Hourly<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Same-Az-Cluster-2nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a><br>
    
    - BYOL<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Same-Az-Cluster-2nic-byol&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
    
    - Using BIG-IQ for Licensing<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=SameAZClusterBigIp-2nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-bigiq-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

  - <a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/cluster/2nic/across-az-ha">Across Availability Zones</a>
    - Hourly<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Across-Az-Cluster-2nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-across-az-cluster-hourly-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a><br>
    
    - BYOL<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Across-Az-Cluster-2nic-byol&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-across-az-cluster-byol-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

    - Using BIG-IQ for Licensing<br><a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=AcrossAZClusterBigIp-2nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-across-az-cluster-bigiq-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

<a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/solutions/autoscale/waf/">**Auto Scaling the BIG-IP Web Application Firewall in AWS**</a>

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=F5-BIGIP-WAF-Autoscale&templateURL=https://s3.amazonaws.com/f5-cft/f5-autoscale-bigip.template"><img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

<a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/solutions/autoscale/ltm/">**Auto Scaling the BIG-IP LTM in AWS**</a>

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=F5-BIGIP-LTM-Autoscale&templateURL=https://s3.amazonaws.com/f5-cft/f5-autoscale-bigip-ltm.template"><img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
  
   
---

### Copyright

Copyright 2014-2017 F5 Networks Inc.


### License


Apache V2.0
~~~~~~~~~~~
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at:

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
