# F5 AWS CloudFormation templates
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-aws-cloudformation.svg)](https://github.com/f5networks/f5-aws-cloudformation/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-aws-cloudformation.svg)](https://github.com/f5networks/f5-aws-cloudformation/issues)

## Introduction

Welcome to the GitHub repository for F5's CloudFormation templates for deploying F5 in Amazon Web Services.  All of the templates in this repository have been developed by F5 Networks engineers.

For information on getting started using F5's CFT templates on GitHub, see [Amazon Web Services: Solutions 101](http://clouddocs.f5.com/cloud/public/v1/aws/AWS_solutions101.html) and the README files in each directory.  

Across all branches in this repository, there are two directories: *supported* and *experimental*.

  - **supported**<br>
  The *supported* directory contains CloudFormation templates that have been created and fully tested by F5 Networks. These templates are fully supported by F5, meaning you can get assistance if necessary from F5 Technical Support via your typical methods.

  - **experimental**<br>
  The *experimental* directory also contains CloudFormation templates that have been created by F5 Networks. However, these templates have not completed full testing and are subject to change. F5 Networks does not offer technical support for templates in the experimental directory, so use these templates with caution.

## Template information
Descriptions for each template are contained at the top of each template in the *Description* key.
For additional information, including how the templates are generated, and assistance in deploying a template, see the README file on the individual template pages.
Standalone and HA production stack templates have been deprecated; a new parameter has been added to existing-stack templates to control deployment of public IP addresses.

### Matrix for tagged releases
F5 has created a matrix that contains all of the tagged releases of the F5 Cloud Formation Templates (CFTs) for Amazon AWS, and the corresponding BIG-IP versions, license types, and throughput levels available for a specific tagged release. See the [AWS Matrix](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/aws-bigip-version-matrix.md).


## Quick Start
The quickstart template allows you to quickly launch an auto scale group of BIG-IP VEs into AWS to demonstrate a typical micro services use case and/or Blue and Green deployment strategy.

For detailed information, we recommend you first see the [Quick Start README file](https://github.com/F5Networks/f5-aws-cloudformation/tree/master/experimental/quickstart)

Or you can use the Launch Stack button to get started:  
<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=quickstart-stack&templateURL=https://f5-cft.s3.amazonaws.com/quickstarts/v0.0.0.3/templates/f5/master.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a> 

  
### All F5 Supported templates for AWS
To see a list of all of our supported AWS CloudFormation templates, see the **[AWS Supported Template index](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/template-index.md)**.


### Troubleshooting and Known Issues
To see steps for troubleshooting common problems with AWS CloudFormation, see the **[Troubleshooting Steps section](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/aws-troubleshooting.md)**. All known issues are on GitHub for better tracking and visibility. See issues with a label of **Known Issues** at https://github.com/f5networks/f5-aws-cloudformation/issues.


---


### Copyright

Copyright2014-2019 F5 Networks Inc.


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
completed and submitted the F5 Contributor License Agreement
