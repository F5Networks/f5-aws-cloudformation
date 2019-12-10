# Deploying the BIG-IQ VE License Manager in AWS - Clustered 2-NIC across Availability Zones: Existing Stack with BYOL Licensing

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-aws-cloudformation.svg)](https://github.com/f5networks/f5-aws-cloudformation/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-aws-cloudformation.svg)](https://github.com/f5networks/f5-aws-cloudformation/issues)

**Contents**
 - [Introduction](#introduction)
 - [Prerequisites](#prerequisites)
 - [Important Configuration Notes](#important-configuration-notes)
 - [Security](#security)
 - [Getting Help](#getting-help)
 - [Deploying the solution](#deploying-the-solution)
 - [Service Discovery](#service-discovery)
 - [Configuration Example](#configuration-example)
 
## Introduction

This solution uses an experimental CloudFormation Template to launch and configure two BIG-IQ 2-NIC VEs in a clustered (hot-standby) configuration across Amazon Availability Zones, using BYOL (bring your own license) licensing.

This is an *existing stack* template, meaning the networking infrastructure MUST be available prior to deploying. See the Template Parameters Section for required networking objects. 

In a BIG-IQ high availability configuration, the BIG-IQ system replicates configuration changes since the last synchronization from the primary device to the secondary device every 30 seconds. If it ever becomes necessary, you can have the secondary peer take over management of the BIG-IP devices. In a 2-NIC implementation, one interface is for management and one is for data-plane traffic, each with a unique public/private IP.  

You can choose one or both of these types of license pools on your BIG-IQ device for licensing your BIG-IP VE devices:
  - A License (Purchase) Pool, which can either be a registration key with a particular number of licenses, or an [ELA](https://www.f5.com/pdf/licensing/big-ip-virtual-edition-enterprise-licensing-agreement-overview.pdf)/subscription pool, which enables self-licensing of BIG-IP virtual editions (VEs), 
  - A Registration Key Pool, which is a pool of single standalone BIG-IP VE registration keys for one or more BIG-IP services. This enables the ability to revoke and reassign a license to BIG-IP VE systems without having to contact F5 to allow the license to be moved.

See the [BIG-IQ documentation](https://support.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/big-iq-centralized-management-device-6-0-1/04.html) for more information on these pool types.

For information on getting started using F5's CFT templates on GitHub, see [Amazon Web Services: Solutions 101](http://clouddocs.f5.com/cloud/public/v1/aws/AWS_solutions101.html).


## Prerequisites and configuration notes
The following are prerequisites for the F5 2-NIC CFT:
  - An existing AWS VPC with two separate Availability Zones, each with two subnets: 
    - Management subnet (called Public in the AWS UI). The subnet for the management network requires a route and access to the Internet for the initial configuration to download the BIG-IP cloud library. 
    - External subnet (called Private in the AWS UI). 
  - The AWS VPC must have **DNS Hostnames** enabled, and the VPC DHCP default option *domain-name = < region >.compute.internal domain-name-servers = AmazonProvidedDNS* is required.
  - Key pair for management access to BIG-IP VE (you can create or import the key pair in AWS), see http://docs.aws.amazon.com/cli/latest/reference/iam/upload-server-certificate.html for information.
  - Because you are deploying the BYOL template, you must have valid BIG-IQ license tokens.
  - An AS3 ARN that contains a BIG-IQ password file in JSON format, which specifies master-key, admin password, and root password to be used during deployment. The JSON file should look like the following:  
  ```json
    {
      "masterPassphrase": "34jkcvni389#494kcx@dfkdi9H",
      "root": "randPass4Root!",
      "admin": "b1gAdminPazz"
    }
  ``` 
  

## Important configuration notes
  - This template creates AWS Security Groups as a part of the deployment. For the internal Security Group, this includes a port for accessing BIG-IQ on port 443.
  - This solution uses the SSH key to enable access to the BIG-IQ system. If you want access to the BIG-IQ web-based Configuration utility, you must first SSH into the BIG-IQ VE using the SSH key you provided in the template.  You can then create a user account with admin-level permissions on the BIG-IP VE to allow access if necessary.
  - This solution uses an AMI image with BIG-IQ v6.0.1 or later. 
  - After deploying the template, if you need to change your BIG-IQ VE password, there are a number of special characters that you should avoid using for F5 product user accounts.  See https://support.f5.com/csp/article/K2873 for details.
  - This template can send non-identifiable statistical information to F5 Networks to help us improve our templates.  See [Sending statistical information to F5](#sending-statistical-information-to-f5).
  - F5 has created a matrix that contains all of the tagged releases of the F5 Cloud Formation Templates (CFTs) for Amazon AWS, and the corresponding BIG-IP versions, license types and throughput levels available for a specific tagged release. See https://github.com/F5Networks/f5-aws-cloudformation/blob/master/aws-bigip-version-matrix.md.
  - These CloudFormation templates incorporate an existing Virtual Private Cloud (VPC). 
  - F5 AWS CFT templates now capture all deployment logs to the BIG-IQ VE in **/var/log/cloud/aws**. Depending on which template you are using, this includes deployment logs (stdout/stderr), Cloud Libs execution logs, recurring solution logs (metrics, failover, and so on), and more.

## Security
This CloudFormation template downloads helper code to configure the BIG-IP system. If you want to verify the integrity of the template, you can open the CFT and ensure the following lines are present. See [Security Details](#security-details) for the exact code in each of the following sections.
  - In the /config/verifyHash section: script-signature and then a hashed signature.
  - In the /config/installCloudLibs.sh section: **tmsh load sys config merge file /config/verifyHash**.
  - In the *filesToVerify* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.
  
Additionally, F5 provides checksums for all of our supported Amazon Web Services CloudFormation templates. For instructions and the checksums to compare against, see https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014.
Note that in order to form a cluster of devices, a secure trust must be established between BIG-IP systems. To establish this trust, we generate and store credentials in an Amazon S3 bucket.

## Recommended AWS instance types and hypervisors
  - For a list of recommended AWS instance types for the BIG-IQ VE, see https://support.f5.com/kb/en-us/products/big-iq-centralized-mgmt/manuals/product/bigiq-ve-supported-hypervisors-matrix.html.

### Getting Help
While this template has been created by F5 Networks, it is in the **experimental** directory and therefore has not completed full testing and is subject to change.  F5 Networks does not offer technical support for templates in the experimental directory. For supported templates, see the templates in the **supported** directory.

**Community Help**  
We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 CloudFormation templates. There are F5 employees who are members of this community who typically monitor the channel Monday-Friday 9-5 PST and will offer best-effort assistance. This slack channel community support should **not** be considered a substitute for F5 Technical Support. See the [Slack Channel Statement](https://github.com/F5Networks/f5-aws-cloudformation/blob/master/slack-channel-statement.md) for guidelines on using this channel.

## Deploying the solution
The easiest way to deploy this CloudFormation template is to use the Launch button.<br>
**Important**: You may have to select the AWS region in which you want to deploy after clicking the Launch Stack button.

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIq-2nic-LicMgmt&templateURL=https://f5-cft.s3.amazonaws.com/f5-existing-stack-cluster-byol-2nic-bigiq-licmgmt.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>

<br>

**Template Parameters**<br>
After clicking the Launch button, you must specify the following parameters.  


| CFT Label | Parameter Name | Required | Description |
| --- | --- | --- | --- |
| VPC | Vpc | Yes | Common VPC for the deployment. |
| Management Subnet AZ1 | managementSubnetAz1 | Yes | Management subnet ID for Availability Zone 1. |
| Management Subnet AZ2 | managementSubnetAz2 | Yes | Management subnet ID for Availability Zone 2. |
| Subnet1 AZ1 | subnet1Az1 | Yes | Public or External subnet ID for Availability Zone 1. |
| Subnet1 AZ1 | subnet1Az2 | Yes | Public or External subnet ID for Availability Zone 2. |
| Custom Image Id | customImageId | No | This parameter allows you to deploy using a custom BIG-IP image if necessary. If applicable, type the AMI Id in this field. **Note**: Unless specifically required, leave the default of **OPTIONAL**. |
| AWS Instance Size | instanceType | Yes | Size for the F5 BIG-IP virtual instance. |
| BIG-IQ License Key 1 | licenseKey1  | Yes | F5 BYOL registration key for your BIG-IQ device |
| BIG-IQ License Key 2 | licenseKey2  | Yes | F5 BYOL registration key for your BIG-IQ device |
| BIG-IP License Pool | licensePoolKeys  | No | Enter a pool name and registration key using the format of name:key. Leave Do_Not_Create if you do not want to create a licensing pool on BIG-IQ at this time. |
| BIG-IQ Reg Key Pool | regPoolKeys | No | Enter a pool name and a list of individual BIG-IP registration keys in the format of name:key,key,key. Leave Do_Not_Create if you do not want to create a reg key pool on BIG-IQ at this time. |
| S3 ARN of the BIG-IQ Password File | bigIqPasswordS3Arn | Yes | ARN of password file in JSON format with master passphrase, admin and root password.
| SSH Key | sshKey | Yes | Name of an existing EC2 KeyPair to enable SSH access to the instance |
| Source Address(es) for Management Access | restrictedSrcAddress | Yes | The IP address range that can be used to SSH to the EC2 instances. |
| Source Address(es) for internal Management Access | restrictedSrcAddressApp | Yes | The IP address range that can be used for management access to the EC2 instances. |
| NTP Server | ntpServer | Yes | NTP server you want to use for this implementation (the default is 0.pool.ntp.org). | 
| Timezone (Olson) | timezone | Yes | Enter the Olson timezone string from /usr/share/zoneinfo. The default is 'UTC'. See the TZ column here (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for legal values. For example, 'US/Eastern'. |
| Application | application | No | Application Tag (the default is f5app). |
| Environment | environment | No | Environment Name Tag (the default is f5env). |
| Group | group | No | Group Tag (the default is f5group). |
| Owner | owner | No | Owner Tag (the default is f5owner). |
| Cost Center | costcenter | No | Cost Center Tag (the default is f5costcenter). |
| Send Anonymous Statistics to F5 | allowUsageAnalytics | No | This deployment can send anonymous statistics to F5 to help us determine how to improve our solutions. If you select **No** statistics are not sent. |

<br>

---




### Sending statistical information to F5
All of the F5 templates now have an option to send anonymous statistical data to F5 Networks to help us improve future templates.  
None of the information we collect is personally identifiable, and only includes:  

- Customer ID: this is a hash of the customer ID, not the actual ID
- Deployment ID: hash of stack ID
- F5 template name
- F5 template version
- Cloud Name
- AWS region 
- BIG-IQ version 
- F5 license type
- F5 Cloud libs version
- F5 script name

This information is critical to the future improvements of templates, but should you decide to select **No**, information will not be sent to F5.

### More documentation
For more information on F5 solutions for AWS, including manual configuration instructions for many of our AWS templates, see our Cloud Docs site: http://clouddocs.f5.com/cloud/public/v1/. You can also see the BIG-IQ documentation at https://support.f5.com/.

## Security Details
This section has the entire code snippets for each of the lines you should ensure are present in your template file if you want to verify the integrity of the helper code in the template.

**/config/verifyHash section**

Note the hashes and script-signature may be different in your template. The important thing to check is that there is a script-signature line present in the location shown.<br>


```json
"/config/verifyHash": {
                "content": {
                  "Fn::Join": [
                    "\n",
                    [
                      "cli script /Common/verifyHash {",
                      "proc script::run {} {",
                      "    set file_path  [lindex $tmsh::argv 1]",
                      "    set expected_hash 73d01a6b4f27032fd31ea7eba55487430ed858feaabd949d4138094c26ce5521b4578c8fc0b20a87edc8cb0d9f28b32b803974ea52b10038f068e6a72fdb2bbd",
                      "    set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]",
                      "    if { $expected_hash eq $computed_hash } {",
                      "        exit 0",
                      "    }",
                      "    exit 1",
                      "}",
                      "    script-signature OGvFJVFxyBm/YlpBsOf8/AIyo5+p7luzrE11v8t7wJ1u24MBeit5pL/McqLxjydPJplymTcJ0qDEtXPZv09TTUF5hrF0g1pJ+z70omzJ6J9kOfOO8lyWP4XU/qM+ywEgAGoc8o8kGjKX01XcmB1e3rq6Mj5gE7CEkxKEcNzF3n5nDIFyBbpG6pJ8kg/7f6gtU14bJo0+ipNAiX+gBmT/10aUKKeJESU5wz+QqnEOE1WuTzdURArxditpk0+qqROZaSULD61w72hEy7kBC/miO+As7q8wjM5/H2yUHLoFLmBWP0jMWqIuzqnG+tgAFjJbZ1UJJDzWiYZK1TG1MsxfPg==",
                      "}"
                    ]
                  ]
                },
                "mode": "000755",
                "owner": "root",
                "group": "root"
              }
```
<br><br>
**/config/installCloudLibs.sh section**


```json
"/config/installCloudLibs.sh": {
                "content": {
                  "Fn::Join": [
                    "\n",
                    [
                      "#!/bin/bash",
                      "echo about to execute",
                      "checks=0",
                      "while [ $checks -lt 120 ]; do echo checking mcpd",
                      "    tmsh -a show sys mcp-state field-fmt | grep -q running",
                      "    if [ $? == 0 ]; then",
                      "        echo mcpd ready",
                      "        break",
                      "    fi",
                      "    echo mcpd not ready yet",
                      "    let checks=checks+1",
                      "    sleep 10",
                      "done",
                      "echo loading verifyHash script",
                      "tmsh load sys config merge file /config/verifyHash",
                      "if [ $? != 0 ]; then",
                      "    echo cannot validate signature of /config/verifyHash",
                      "    exit",
                      "fi",
                      "echo loaded verifyHash",
                      "echo verifying f5-cloud-libs.targ.gz",
                      "tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz",
                      "if [ $? != 0 ]; then",
                      "    echo f5-cloud-libs.tar.gz is not valid",
                      "    exit",
                      "fi",
                      "echo verified f5-cloud-libs.tar.gz",
                      "echo expanding f5-cloud-libs.tar.gz",
                      "tar xvfz /config/cloud/f5-aws-autoscale-cluster.tar.gz -C /config/cloud",
                      "tar xvfz /config/cloud/asm-policy-linux.tar.gz -C /config/cloud",
                      "tar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/aws/node_modules",
                      "cd /config/cloud/aws/node_modules/f5-cloud-libs",
                      "echo installing dependencies",
                      "npm install --production /config/cloud/f5-cloud-libs-aws.tar.gz",
                      "touch /config/cloud/cloudLibsReady"
                    ]
                  ]
                },
                "mode": "000755",
                "owner": "root",
                "group": "root"
              }
```




## Filing Issues
If you find an issue, we would love to hear about it. 
You have a choice when it comes to filing issues:
  - Use the **Issues** link on the GitHub menu bar in this repository for items such as enhancement or feature requests and non-urgent bug fixes. Tell us as much as you can about what you found and how you found it.
  - Contact us at [solutionsfeedback@f5.com](mailto:solutionsfeedback@f5.com?subject=GitHub%20Feedback) for general feedback or enhancement requests. 
  - Use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 cloud templates.  There are F5 employees who are members of this community who typically monitor the channel Monday-Friday 9-5 PST and will offer best-effort assistance.
  - For templates in the **supported** directory, contact F5 Technical support via your typical method for more time sensitive changes and other issues requiring immediate support.



## Copyright

Copyright2014-2019 F5 Networks Inc.


## License


### Apache V2.0

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

### Contributor License Agreement

Individuals or business entities who contribute to this project must have
completed and submitted the F5 Contributor License Agreement.
