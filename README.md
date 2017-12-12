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

### Matrix for tagged releases
F5 has created a matrix that contains all of the tagged releases of the F5 Cloud Formation Templates (CFTs) for Amazon AWS, and the corresponding BIG-IP versions, license types, and throughput levels available for a specific tagged release. See https://github.com/F5Networks/f5-aws-cloudformation/blob/master/aws-bigip-version-matrix.md.


## List of Supported F5 CloudFormation templates for AWS deployments
The following is a list of the current *supported* F5 CloudFormation templates. Click the links below to view the README files which include the Launch buttons and additional information, or click the **Launch Stack** buttons to immediately launch the stack. Because individual templates may have specific prerequisites, we strongly recommend you view the README file before attempting to launch a template. 

**Important**: You may have to select the AWS region in which you want to deploy after clicking the Launch Stack button
<br><br>
<a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/1nic">**Standalone BIG-IP VE - Single NIC**</a>
- **Hourly**, which uses pay-as-you-go hourly billing  
  - Launch the *existing stack* template which includes an external IP address (typical):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-1nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

  - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/1nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-Hourly-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-hourly-1nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>  

- **BYOL** (bring your own license), which allows you to use an existing BIG-IP license.   
   - Launch the *existing stack* template which includes an external IP address (typical):  
      <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-1nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
   - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/1nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-BYOL-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-byol-1nic-bigip.template">    
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>  

- **BIG-IQ for licensing**, which allows you to launch the template using an existing BIG-IQ device with a pool of licenses to license the BIG-IP VE(s).  
   - Launch the *existing stack* template which includes an external IP address (typical):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-bigiq-1nic-bigip.template">  
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
   - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/1nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-1nic-BIGIQ-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-bigiq-1nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a> 
 

<a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/2nic">**Standalone BIG-IP VE - 2 NICs**</a>
- **Hourly**, which uses pay-as-you-go hourly billing  
  - Launch the *existing stack* template which includes an external IP address (typical):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-2nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

  - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/2nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-Hourly-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-hourly-2nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>  

- **BYOL** (bring your own license), which allows you to use an existing BIG-IP license.   
   - Launch the *existing stack* template which includes an external IP address (typical):  
      <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
   - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/2nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BYOL-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-byol-2nic-bigip.template">    
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>  

- **BIG-IQ for licensing**, which allows you to launch the template using an existing BIG-IQ device with a pool of licenses to license the BIG-IP VE(s).  
   - Launch the *existing stack* template which includes an external IP address (typical):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-bigiq-2nic-bigip.template">  
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
   - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/2nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BIGIQ-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-bigiq-2nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

<a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/3nic">**Standalone BIG-IP VE - 3 NICs**</a>
- **Hourly**, which uses pay-as-you-go hourly billing  
  - Launch the *existing stack* template which includes an external IP address (typical):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-3nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

  - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/3nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-Hourly-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-hourly-3nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>  

- **BYOL** (bring your own license), which allows you to use an existing BIG-IP license.   
   - Launch the *existing stack* template which includes an external IP address (typical):  
      <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-BYOL&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-3nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
   - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/3nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-BYOL-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-byol-3nic-bigip.template">    
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>  

- **BIG-IQ for licensing**, which allows you to launch the template using an existing BIG-IQ device with a pool of licenses to license the BIG-IP VE(s).  
   - Launch the *existing stack* template which includes an external IP address (typical):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-bigiq-3nic-bigip.template">  
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
   - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/standalone/3nic#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-3nic-BIGIQ-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-bigiq-3nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a> 



**Clustered BIG-IP VE - 2 NICs**
  - <a href="https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/cluster/2nic/same-az-ha">Same Availability Zone</a>
    - **Hourly**, which uses pay-as-you-go hourly billing  
      - Launch the *existing stack* template which includes an external IP address (typical):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Same-Az-Cluster-2nic-Hourly&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
      - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/cluster/2nic/same-az-ha#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Same-Az-Cluster-2nic-Hourly-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-same-az-cluster-hourly-2nic-bigip.template">  
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>  
    - **BYOL** (bring your own license), which allows you to use an existing BIG-IP license.   
      - Launch the *existing stack* template which includes an external IP address (typical):  
        <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Same-Az-Cluster-2nic-byol&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
      - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/cluster/2nic/same-az-ha#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Same-Az-Cluster-2nic-byol&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-same-az-cluster-byol-2nic-bigip.template">    
   <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>  
    - **BIG-IQ for licensing**, which allows you to launch the template using an existing BIG-IQ device with a pool of licenses to license the BIG-IP VE(s).  
      - Launch the *existing stack* template which includes an external IP address (typical):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=SameAZClusterBigIp-2nic-BIGIQ&templateURL=https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-bigiq-2nic-bigip.template">  
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
      - Launch the *production stack* template, which does not include a public IP address (as described in the [README](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/supported/cluster/2nic/same-az-ha#introduction)):  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=SameAZClusterBigIp-2nic-BIGIQ-Prod&templateURL=https://s3.amazonaws.com/f5-cft/f5-prod-stack-same-az-cluster-bigiq-2nic-bigip.template">  
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

<table>
 <tr>
  <td align=center>:warning: <strong>IMPORTANT<strong> :warning:  </td>
 </tr>
 <tr>
  <td>If you used a CFT template prior to [release 2.7.1](https://github.com/F5Networks/f5-aws-cloudformation/releases/tag/v2.7.1), BIG-IP virtual servers configured with a Client SSL profile may be vulnerable to an Adaptive Chosen Ciphertext attack (AKA Bleichenbacher attack). For complete information on this vulnerability, see https://support.f5.com/csp/article/K21905460. <br>F5 has released hotfixes for all vulnerable releases. All of he templates in the current release in this repository use non-vulnerable BIG-IP VE images.  If you are using a BIG-IP image launched from a previous version of a template, use the following guidance:<br>  
   <ul>
    <li><em>If you have an existing BIG-IP VE deployment in AWS</em>  <br>See the <a href="https://support.f5.com/csp/article/K21905460">Security Advisory</a>, which contains information about upgrading your BIG-IP VE to a non-vulnerable version.</li>
    <li><em>For <strong>new</strong> BIG-IP VE deployments in AWS</em><br> The F5 CFT templates in [release 2.7.1](https://github.com/F5Networks/f5-aws-cloudformation/releases/tag/v2.7.1) and later use non-vulnerable images. We recommending using the templates in the [latest release](https://github.com/F5Networks/f5-aws-cloudformation/releases) for new deployments.</li>
    <li><em>For <strong>new</strong> BIG-IP VE deployments using a template in an older tagged release on GitHub</em><br>  If you have a specific need for using an older F5 CFT template, see <a href="aws-update-bigip-image.md">Changing the BIG-IP VE image in an F5 CFT template</a> for instructions on updating the BIG-IP images referenced in the template.</li>
   </ul></td>
 </tr>
 </table>

### Copyright

Copyright 2014-2017 F5 Networks Inc.


### License


## Apache V2.0

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.


## Contributor License Agreement

Individuals or business entities who contribute to this project must have
completed and submitted the `F5 Contributor License Agreement`