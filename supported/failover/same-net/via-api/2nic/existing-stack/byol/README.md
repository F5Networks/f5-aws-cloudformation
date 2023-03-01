# Deploying the BIG-IP VE in AWS - Clustered 2 NIC - Same Availability Zone: Existing Stack with BYOL Licensing

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
This solution uses a CloudFormation Template to launch and configure two BIG-IP 2-NIC VEs in a clustered, highly available configuration in an Amazon Availability Zone, using BYOL (bring your own license) licensing.

This is an *existing stack* template, meaning the networking infrastructure MUST be available prior to deploying. See the Template Parameters Section for required networking objects. By default, the template will create and attach Public IP Address(es) to the BIG-IP interface(s). Where dictated by security policy or in deployments where accessing resources does not require a Public IP address on the BIG-IP VE, such as users connecting to internal applications using a VPN, set the **provisionPublicIP** parameter to 'No', which will not create Public IP Address(es).

When you deploy your applications behind a HA pair of F5 BIG-IP VEs, the BIG-IP VE instances are all in Active-Standby, and are used as a single device for failover. If one device becomes unavailable, the standby takes over traffic management duties, ensuring you have the highest level of availability for your applications. The BIG-IP VEs have the <a href="https://f5.com/products/big-ip/local-traffic-manager-ltm">Local Traffic Manager</a> (LTM) module, so you can also configure the BIG-IP VE to enable F5's L4/L7 security features, access control, and intelligent traffic management.

In a 2-NIC implementation, one interface is for management and one is for data-plane traffic, each with a unique public/private IP. Traffic flows from the BIG-IP VE to the application servers.

For information on getting started using F5's CFT templates on GitHub, see [Amazon Web Services: Solutions 101](http://clouddocs.f5.com/cloud/public/v1/aws/AWS_solutions101.html).

## Prerequisites
The following are prerequisites for the F5 clustered 2-NIC CFT:
  - An AWS VPC with two subnets: 
    - Management subnet (the subnet for the management network requires a route and access to the Internet for the initial configuration to download the BIG-IP cloud library).
    - External subnet (the subnet for the external network requires a route and access to the Internet for onboarding BIG-IP).
  - Key pair for management access to BIG-IP VE (you can create or import the key pair in AWS), see http://docs.aws.amazon.com/cli/latest/reference/iam/upload-server-certificate.html for information.
  - The AWS VPC must have **DNS Hostnames** enabled, and the VPC DHCP default option *domain-name = < region >.compute.internal domain-name-servers = AmazonProvidedDNS* is required.
  - Because you are deploying the BYOL template, you must have valid BIG-IP license tokens.
  
## Important configuration notes 
  - This solution template provides an initial deployment only for an "infrastructure" use case (meaning that it does not support managing the entire deployment exclusively via the template's "Update-Stack" function). This solution leverages cloud-init to send the instance user_data, which is only used to provide an initial BIG-IP configuration and not as the primary configuration API for a long-running platform. Although "Update-Stack" can be used to update some cloud resources, as the BIG-IP configuration needs to align with the cloud resources, like IPs to NICs, updating one without the other can result in inconsistent states, while updating other resources, like the image name or instance type, can trigger an entire instance redeployment. For instance, to upgrade software versions, traditional in-place upgrades should be leveraged. See [AskF5 Knowledge Base](https://support.f5.com/csp/article/K84554955) for more information.
  - There are new options for BIG-IP license bundles.
  - F5 has created a matrix located [here](https://github.com/F5Networks/f5-aws-cloudformation/blob/main/aws-bigip-version-matrix.md) that contains all of the tagged releases of the F5 Cloud Formation Templates (CFTs) for Amazon AWS, and the corresponding BIG-IP versions, license types, and throughput levels available for a specific tagged release. 
  - Beginning with release 3.3.0, the BIG-IP image names have changed (previous options were Good, Better, and Best). Now you choose a BIG-IP VE image based on whether you need [LTM](https://www.f5.com/products/big-ip-services/local-traffic-manager) only or All modules available (including [WAF](https://www.f5.com/products/security/advanced-waf), [AFM](https://www.f5.com/products/security/advanced-firewall-manager), etc.), and if you need 1 or 2 boot locations. Use 2 boot locations if you expect to upgrade the BIG-IP VE in the future. If you do not need room to upgrade (if you intend to create a new instance when a new version of BIG-IP VE is released), use an image with 1 boot location. See this [Matrix](https://clouddocs.f5.com/cloud/public/v1/matrix.html#amazon-web-services) for recommended AWS instance types. For custom images (for example, different versions from the marketplace, clones or those created by the [F5 BIG-IP Image Generator](https://github.com/f5devcentral/f5-bigip-image-generator/)), update the **customImageId** parameter. To see a list of available BIG-IP images and IDs from the marketplace (for example in "us-east-1"), you can run the AWS command below:
    ``` 
    $ aws ec2 describe-images --owners aws-marketplace --region us-east-1 --filters "Name=description,Values=F5*BIGIP**" --query 'Images[*].[ImageId,Description,CreationDate]' 
    ```
  - All supported versions of F5 CloudFormation templates include Application Services 3 Extension (AS3) on the BIG-IP VE. As of release 4.1.2, all supported templates give the option of including the URL of an AS3 declaration, which you can use to specify the BIG-IP configuration you want on your newly created BIG-IP VE(s). See the [AS3 documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/) for details on how to use AS3.
  - All supported versions of AWS F5 CloudFormation Failover templates now include F5 Cloud Failover Extension (CFE) on the BIG-IP VE. The F5 Cloud Failover Extension (CFE) is an iControl LX extension that provides L3 failover functionality in cloud environments, effectively replacing Gratuitous ARP (GARP). Cloud Failover Extension uses a declarative model, meaning you provide a JSON declaration using a single REST API call. The declaration represents the configuration that Cloud Failover Extension is responsible for creating on a BIG-IP system. This template constructs and posts required declaration to CFE required to handle IP failover. However, if you you wish to configure route failover CFE feature, you will need to do 2 additional steps. 1) Tag appropriate route tables with key/value: "f5_cloud_failover_label/your stack name". 2) Post modified declaration with correct affected CIDR blocks. Note: You can use GET method to url https://yourBigIP/mgmt/shared/cloud-failover/declare to retrieve existing CFE declaration. See the [CFE documentation](https://clouddocs.f5.com/products/extensions/f5-cloud-failover/latest/) for details on how to use CFE.
  - This template uses [F5 BIG-IP Runtime Init](https://github.com/F5Networks/f5-bigip-runtime-init) to install F5 Automation Toolchain packages (AS3, DO, CFE, FAST, and TS). You can update the version of one or more packages by editing the UserData property of the BIG-IP instance resource(s). For example: To update the AS3 package to the latest version, click on the [Github release page](https://github.com/F5Networks/f5-appsvcs-extension/releases) for the f5-appsvcs-extension. In the instance UserData property, in the install_operations section, update the AS3 extensionVersion value to the desired version and the extensionHash value to contents of the RPM sha256 file located in the release assets for that version. You can also add more packages to be installed using the same procedure.
  - This template creates AWS Security Groups as a part of the deployment. For the external Security Group, this includes a port for accessing your applications on port 80/443. If your applications need additional ports, you must add those to the external Security Group created by the template. For instructions on adding ports, see the AWS documentation.
  - This solution uses the SSH key to enable access to the BIG-IP system(s). If you want access to the BIG-IP web-based Configuration utility, you must first SSH into the BIG-IP VE using the SSH key you provided in the template. You can then create a user account with admin-level permissions on the BIG-IP VE to allow access if necessary.
  - This template supports service discovery via the Application Services 3 Extension (AS3). See the [Service Discovery section](#service-discovery) for details.
  - This template supports telemetry streaming via the F5 Telemetry Streaming extension (TS). See [Telemetry Streaming](#telemetry-streaming) for details.
  - In order to pass traffic from your clients to the servers, after launching the template you must create virtual servers on the BIG-IP VE. See [Creating a virtual server](#creating-virtual-servers-on-the-big-ip-ve).
  - After deploying the template, if you need to change your BIG-IP VE password, there are a number of special characters that you should avoid using for F5 product user accounts. See https://support.f5.com/csp/article/K2873 for details.
  - F5 AWS CFT templates now capture all deployment logs to the BIG-IP VE in **/var/log/cloud/aws**. Depending on which template you are using, this includes deployment logs (stdout/stderr), Cloud Libs execution logs, recurring solution logs (metrics, failover, and so on), and more.
  - This template can send non-identifiable statistical information to F5 Networks to help us improve our templates. See [Sending statistical information to F5](#sending-statistical-information-to-f5).
  - This template supports disabling the auto-phonehome system setting via the allowPhoneHome parameter. See [Overview of the Automatic Update Check and Automatic Phone Home features](https://support.f5.com/csp/article/K15000) for more information.


## Security
This CloudFormation template downloads helper code to configure the BIG-IP system. If you want to verify the integrity of the template, you can open the CFT and ensure the following lines are present. See [Security Detail](#securitydetail) for the exact code in each of the following sections.
  - In the /config/verifyHash section: script-signature and then a hashed signature.
  - In the /config/installCloudLibs.sh section: **tmsh load sys config merge file /config/verifyHash**.
  - In the *filesToVerify* variable: ensure this includes **tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz**.
  
Additionally, F5 provides checksums for all of our supported Amazon Web Services CloudFormation templates. For instructions and the checksums to compare against, see https://community.f5.com/t5/crowdsrc/checksums-for-f5-supported-cloud-templates-on-github/ta-p/284471.
**NOTE**: In order to form a cluster of devices, a secure trust must be established between BIG-IP systems. To establish this trust, we generate and store credentials as credentials/primary in an Amazon S3 bucket. Upon completion of a successful deployment, these credentials, as well as the corresponding local service account user, are deleted by the f5-cloud-libs cluster provider. If for some reason these credentials are not deleted, you may remove them at any time following deployment.
## Tested BIG-IP versions
The following table lists the versions of BIG-IP that have been tested and validated against F5 AWS solution templates.

| BIG-IP Version | Build | Solution | Status | Notes |
| --- | --- | --- | --- | --- |
| 16.1.3.3 | 0.0.3 | Standalone, Failover, Autoscale | Validated | |
| 15.1.8.1 | 0.0.3 | Standalone, Failover, Autoscale | Validated | |
| 14.1.5.3 | 0.0.5 | Standalone, Failover, Autoscale | Validated | |
| 13.1.5.1 | 0.0.2 | Standalone, Failover, Autoscale | Not Validated | F5 CFE requires BIG-IP 14.1 or later |
| 12.1.6 | 0.0.9 | Standalone, Failover, Autoscale | Not Validated | F5 CFE requires BIG-IP 14.1 or later |

## Supported instance types and hypervisors
  - For a list of supported AWS instance types for this solutions, see https://clouddocs.f5.com/cloud/public/v1/matrix.html#amazon-web-services.

  - For a list versions of the BIG-IP Virtual Edition (VE) and F5 licenses that are supported on specific hypervisors and AWS, see https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ve-supported-hypervisor-matrix.html.

### Getting Help
**F5 Support**
Because this template has been created and fully tested by F5 Networks, it is fully supported by F5. This means you can get assistance if necessary from [F5 Technical Support](https://support.f5.com/csp/article/K25327565). You can modify the template itself if necessary, but if you modify any of the code outside of the lines ### START CUSTOM TMSH CONFIGURATION and ### END CUSTOM TMSH CONFIGURATION the template is no longer supported by F5.

## Deploying the solution

You have two options for deploying this template: 
  - Using the [Launch Stack button](#installing-the-image-using-the-aws-launch-stack-button) 
  - Using the [AWS CLI](#installing-the-template-using-the-aws-cli)

### Installing the image using the AWS Launch Stack button
The easiest way to deploy this CloudFormation template is to use the Launch button.<br>
**Important**: You may have to select the AWS region in which you want to deploy after clicking the Launch Stack button.

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BIGIP-Same-Az-Cluster-2nic-byol&templateURL=https://f5-cft.s3.amazonaws.com/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></a>
<br>

**Template Parameters**<br>
After clicking the Launch button, you must specify the following parameters.


| CFT Label | Parameter Name | Required | Description |
| --- | --- | --- | --- |
| VPC | Vpc | Yes | Common VPC for the deployment |
| Management Subnet AZ1 | managementSubnetAz1 | Yes | Management subnet ID |
| Subnet1 AZ1 | subnet1Az1 | Yes | Public or External subnet ID |
| BIG-IP Image Name | imageName | Yes | Image names starting with **All** have all BIG-IP modules available. Image names starting with **LTM** have only the LTM module available. Use Two Boot Locations if you expect to upgrade the BIG-IP VE in the future. If you do not need room to upgrade (if you intend to create a new instance when a new version of BIG-IP VE is released), use one Boot Location. |
| Custom Image Id | customImageId | No | This parameter allows you to deploy using a custom BIG-IP image if necessary. If applicable, type the AMI Id in this field. **Note**: Unless specifically required, leave the default of **OPTIONAL**. |
| AWS Instance Size | instanceType | Yes | Size for the F5 BIG-IP virtual instance. |
| License Key1 | licenseKey1 | Yes | Type or paste your F5 BYOL regkey. |
| License Key2 | licenseKey2 | Yes | Type or paste your F5 BYOL regkey for the second BIG-IP VE. |
| SSH Key | sshKey | Yes | Name of an existing EC2 KeyPair to enable SSH access to the instance |
| Source Address(es) for Management Access | restrictedSrcAddress | Yes | This field restricts management access to a specific network or address. Enter an IP address or address range in CIDR notation. Please do NOT use "0.0.0.0/0". Instead, restrict the IP address range to your client or trusted network, for example "55.55.55.55/32". Production should never expose the BIG-IP Management interface to the Internet. |
| Source Address(es) for Web Application Access (80/443) | restrictedSrcAddressApp | Yes | The IP address range that can be used for management access to the EC2 instances. |
| NTP Server | ntpServer | Yes | NTP server you want to use for this implementation (the default is 0.pool.ntp.org). | 
| Timezone (Olson) | timezone | Yes | Enter the Olson timezone string from /usr/share/zoneinfo. The default is 'UTC'. See the TZ column here (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for legal values. For example, 'US/Eastern'. |
| BIG-IP Modules | bigIpModules | No | Comma separated list of modules and levels to provision, for example, 'ltm:nominal,asm:nominal' |
| Application | application | No | Application Tag (the default is f5app). |
| Environment | environment | No | Environment Name Tag (the default is f5env). |
| Group | group | No | Group Tag (the default is f5group). |
| Owner | owner | No | Owner Tag (the default is f5owner). |
| Cost Center | costcenter | No | Cost Center Tag (the default is f5costcenter). |
| Send Anonymous Statistics to F5 | allowUsageAnalytics | No | This deployment can send anonymous statistics to F5 to help us determine how to improve our solutions. If you select **No** statistics are not sent. |
| AS3 Declaration URL | declarationUrl | No | URL for the [AS3](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/) declaration JSON file to be deployed. Leave as **none** to deploy without a service configuration. |
| Provision Public IP addresses for the BIG-IP interfaces | provisionPublicIP | Yes | Whether or not to provision Public IP Addresses for the BIG-IP Network Interfaces. By Default Public IP address(es) are provisioned. | 
<br>

### Installing the template using the AWS CLI
If you want to deploy the template using the AWS CLI(aws-cli/1.11.165), use the example **deploy_via_bash.sh** script available [in this repository](https://github.com/F5Networks/f5-aws-cloudformation/blob/main/supported/failover/same-net/via-api/2nic/existing-stack/byol/deploy_via_bash.sh). Replace the static items (or make them parameters).

---

### Service Discovery

This template previously supported configuring service discovery using the f5.service_discovery iApp template. That iApp has been deprecated and removed from this template. You can now configure service discovery using the F5 AS3 extension, which is installed by all Cloudformation templates by default. See the official AS3 [documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/service-discovery.html) and the iApp migration [guide](https://github.com/F5Networks/f5-aws-cloudformation/blob/main/iapp-migration.md) for more information and examples.

### Telemetry Streaming

This template previously supported configuring device telemetry using the f5.cloud_logger iApp template. That iApp has been deprecated and removed from this template. You can now configure telemetry streaming using the F5 Telemetry Streaming extension. See the official TS [documentation](https://clouddocs.f5.com/products/extensions/f5-telemetry-streaming/latest/) and the iApp migration [guide](https://github.com/F5Networks/f5-aws-cloudformation/blob/main/iapp-migration.md) for installation steps and examples.

## Creating virtual servers on the BIG-IP VE

In order to pass traffic from your clients to the servers through the BIG-IP system, you must create virtual servers on the BIG-IP VE. To create a BIG-IP virtual server you need to know the AWS secondary private IP addresses for each BIG-IP VE created by the template. If you need additional virtual servers for your applications/servers, you can add more secondary private IP addresses in AWS, and corresponding virtual servers on the BIG-IP system. See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/MultipleIP.html for information on multiple IP addresses.

**To create virtual servers on the BIG-IP system**

1. Once your BIG-IP VE has launched, open the BIG-IP VE Configuration utility.
2. On the Main tab, click **Local Traffic > Virtual Servers** and then click the **Create** button.
3. In the **Name** field, give the Virtual Server a unique name.
4. In the **Destination/Mask** field, type the AWS secondary private IP address.
5. In the **Service Port** field, type the appropriate port. 
6. Configure the rest of the virtual server as appropriate.
7. In the Resources section, from the **Default Pool** list, select the name of the pool you want to use.
8. Click the **Finished** button.
9. Repeat as necessary.

## Configuration Example

The following is a simple configuration diagram for this clustered, 2-NIC deployment. This solution uses IAM roles for authentication.<br>
![Clustered 2-NIC configuration example](../../images/caws-failover-same-net-2nic-multiple-vips-animated.gif)

### Sending statistical information to F5
All of the F5 templates now have an option to send anonymous statistical data to F5 Networks to help us improve future templates.
None of the information we collect is personally identifiable, and only includes:

- Customer ID: this is a hash of the customer ID, not the actual ID
- Deployment ID: hash of stack ID
- F5 template name
- F5 template version
- Cloud Name
- AWS region 
- BIG-IP version 
- F5 license type
- F5 Cloud libs version
- F5 script name

This information is critical to the future improvements of templates, but should you decide to select **No**, information will not be sent to F5.

### In-Place upgrade of BIG-IP v13 instances

When performing an in-place upgrade from BIG-IP software v13.x, you must complete the following steps to ensure that all the components required for failover are copied to the volume where the new version of BIG-IP is installed. To ensure traffic processing is not interrupted, F5 highly recommends upgrading the standby device, verifying failover functionality, and then upgrading the previously active device. 

From the volume to be upgraded on the standby device, you must edit **cs.dat** to allow inclusion of all files in **/config/cloud** in UCS backup.

1. Remount the /usr directory as writable:
  ``mount -o remount,rw /usr``

2. Back up the cs.dat file:
 ``cp /usr/libdata/configsync/cs.dat /usr/libdata/configsync/cs.dat.bak``

3. Edit the cs.dat file:
``vi /usr/libdata/configsync/cs.dat``

4. In cs.dat, find the entry similar to the one below (the number between save and ignore may differ):  
**save.10100.ignore = (/config/cloud/*)**

5. Change **ignore** to **file** in the save key, and remove the parentheses from the value:
``save.10100.file = /config/cloud/*``

6. Save the cs.dat file and exit the editor.

7. Remount the **/usr** directory as read-only:
``mount -o remount,ro /usr``

8. Create a [UCS archive](https://support.f5.com/csp/article/K13132) in the BIG-IP UI (accept defaults):
**System > Archives > Create > myUCS** 

9. Download myUCS.ucs locally.

10. Install new ISO and reboot into upgraded volume.

11. Boot into the newly upgraded volume.

12. After verifying failover functionality, repeat steps 1-11 on the now-standby BIG-IP device.

13. Following the upgrade, all the necessary files should be present and failover should work normally. To manually restore the UCS archive you created previously, use the following steps:
    - From the upgraded volume, upload UCS file: **System > Archives > Upload > myUCS.uss**
    - Restore the previously created UCS archive: **System > Archives > myUCS.ucs > Restore**

### More documentation
For more information on F5 solutions for AWS, including manual configuration instructions for many of our AWS templates, see our Cloud Docs site: http://clouddocs.f5.com/cloud/public/v1/.

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
  - Use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 cloud templates. There are F5 employees who are members of this community who typically monitor the channel Monday-Friday 9-5 PST and will offer best-effort assistance.
  - For templates in the **supported** directory, contact F5 Technical support via your typical method for more time sensitive changes and other issues requiring immediate support.



## Copyright

Copyright 2014-2022 F5 Networks Inc.


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
