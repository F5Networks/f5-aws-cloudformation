# F5 AWS CloudFormation Templates 1.0
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-aws-cloudformation.svg)](https://github.com/f5networks/f5-aws-cloudformation/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-aws-cloudformation.svg)](https://github.com/f5networks/f5-aws-cloudformation/issues)

| :eyes: | ***Notice***: F5 BIG-IP Cloud Solution Templates v1 (CSTv1) have reached their End of Life (EoL) and have been replaced by our next-generation templates available in the [Cloud Templates 2.0 GitHub repo](https://github.com/F5Networks/f5-aws-cloudformation-v2). We recommend you adopt the next-generation templates as soon as is feasible. |
|---------------|:------------------------|  

## Introduction

Welcome to the GitHub repository for F5's CloudFormation Templates 1.0 for deploying F5 in Amazon Web Services. All of the templates in this repository have been developed by F5 Networks engineers.

For information on getting started using F5's CFT templates on GitHub, see [Amazon Web Services: Solutions 101](http://clouddocs.f5.com/cloud/public/v1/aws/AWS_solutions101.html) and the README files in each directory.  

This repository contains one main directory: supported.

The *supported* directory contains our legacy AWS CloudFormation templates (CFTs) that have been created and fully tested by F5 Networks. These legacy cloud solution templates (CST1) are fully supported by F5, meaning you can get assistance if necessary from F5 Technical Support via your typical methods. These legacy templates are now in maintenance mode and are being replaced by our next-generation cloud solution templates (CST2) available at https://github.com/F5Networks/f5-aws-cloudformation-v2. We recommend you adopt the next-generation templates as soon as is feasible.

  - Maintenance mode does NOT mean we are removing nor disabling legacy templates.
  - Customers are free to continue using legacy cloud templates.
  - Legacy cloud templates are officially in sustaining/maintenance mode.
  - Package updates and critical bug fixes will be considered for maintenance mode cloud templates.
  - TMOS 16.1 is the final TMOS version for which legacy cloud verification testing will take place.
  - No new features nor legacy cloud templates will be developed.


## Template information
Descriptions for each template are contained at the top of each template in the *Description* key.
For additional information, including how the templates are generated, and assistance in deploying a template, see the README file on the individual template pages.
Standalone and HA production stack templates have been deprecated; a new parameter has been added to existing-stack templates to control deployment of public IP addresses.

### Matrix for tagged releases
F5 has created a matrix that contains all of the tagged releases of the F5 Cloud Formation Templates (CFTs) for Amazon AWS, and the corresponding BIG-IP versions, license types, and throughput levels available for a specific tagged release. See the [AWS Matrix](https://github.com/F5Networks/f5-aws-cloudformation/blob/main/aws-bigip-version-matrix.md).

  
### All F5 Supported templates for AWS
To see a list of all of our supported AWS CloudFormation templates, see the **[AWS Supported Template index](https://github.com/F5Networks/f5-aws-cloudformation/blob/main/template-index.md)**.

### Note on IMDSv2
These templates now use IMDSv2 to access AWS metadata from within instances. IMDSv2 uses session-oriented requests instead of the request/response model used by IMDSv1. Please read more about [IMDSv2 here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html). This does not affect how the templates are deployed but makes your deployments secure against various types of attacks. Please read more on the topic [here](https://aws.amazon.com/blogs/security/defense-in-depth-open-firewalls-reverse-proxies-ssrf-vulnerabilities-ec2-instance-metadata-service/).


### Troubleshooting and Known Issues
To see steps for troubleshooting common problems with AWS CloudFormation, see the **[Troubleshooting Steps section](https://github.com/F5Networks/f5-aws-cloudformation/blob/main/aws-troubleshooting.md)**. All known issues are on GitHub for better tracking and visibility. See issues with a label of **Known Issues** at https://github.com/f5networks/f5-aws-cloudformation/issues.


---


### Copyright

Copyright 2014-2022 F5 Networks Inc.


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
