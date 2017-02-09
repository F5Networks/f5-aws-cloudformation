# Auto scaling the BIG-IP VE Web Application Firewall in AWS
[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

## Introduction
This project implements auto scaling of BIG-IP Virtual Edition Web Application Firewall (WAF) systems in Amazon Web Services using the AWS CloudFormation template **f5-autoscale-bigip.template**. As traffic increases or decreases, the number of BIG-IP VE instances automatically increases or decreases accordingly.

See the [Configuration Example](#config) section for a configuration diagram and more information for this solution.<br>
See the [Security Blocking Levels](#blocking) section for a description of the blocking levels for the Web Application Firewall presented in the template.

## BIG-IP deployment and configuration

All BIG-IP VE instances deploy with a single interface (NIC) attached to a public subnet. This single interface processes both management and data plane traffic.  The <a href="https://f5.com/products/big-ip/local-traffic-manager-ltm">BIG-IP Local Traffic Manager</a> (LTM) and <a href="https://f5.com/products/big-ip/application-security-manager-asm">Application Security Manager</a> (ASM) provide advanced traffic management and security functionality. The CloudFormation template uses the default **Best 1000Mbs** image available in the AWS marketplace to license these modules.
The template performs all of the BIG-IP VE configuration and synchronization when the device boots using `Cloud-Init`. In general, Cloud-Init is used to:

- Set the BIG-IP hostname, NTP, and DNS settings
- Configure an IAM (Identity and Access Management) role with policies allowing the BIG-IP to make authenticated calls to AWS HTTPS endpoints.
- Create a HTTP virtual server with a Web Application Firewall policy
- Deploy integration with EC2 Autoscale and CloudWatch services for scaling of the BIG-IP tier.

## Prerequisites
The following are prerequisites for this solution:
  - An AWS VPC with a public subnet and an ELB sandwich (one ELB front of the BIG-IP(s) and one ELB behind the BIG-IP(s))
  - Key pair for SSH access to BIG-IP VE (you can create or import in AWS)
  - An AWS Security Group with the following inbound rules:
    - Port 22 for SSH access to the BIG-IP VE
    - Port 8443 (or other port) for accessing the BIG-IP web-based Configuration utility
    - A port for accessing your applications via the BIG-IP virtual server

## Security
This CloudFormation template downloads helper code to configure the BIG-IP system. If your organization is security conscious and you want to verify the integrity of the template, you can open the CFT and ensure the following lines are present. See [Security Detail](#securitydetail) for the exact code in each of the following sections.
  - In the */config/verifyHash* section: **script-signature** and then a hashed signature
  - In the */config/installCloudLibs.sh* section **"tmsh load sys config merge file /config/verifyHash"**
  
In order to form a cluster of devices, a secure trust must be established between BIG-IP systems. To establish this trust, we generate and store credentials in an Amazon S3 bucket. You must not delete these credentials from the S3 bucket.

### Help 

We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 CloudFormation templates.  This channel is typically monitored Monday-Friday 9-5 PST by F5 employees who will offer best-effort support.<br>
While this template has been created by F5 Networks, it is in the experimental directory and therefore has not completed full testing and is subject to change.  F5 Networks does not offer technical support for templates in the **experimental** directory. For supported templates, see the templates in the supported directory.


### Installation
Download the CloudFormation template from https://github.com/f5networks and use it to create a stack in AWS CloudFormation either using the AWS Console or AWS CLI

**AWS Console**

 From the AWS Console main page: 
   1. Under AWS Services, click **CloudFormation**.
   2. Click the **Create Stack** button 
   3. In the Choose a template area, click **Upload a template to Amazon S3**.
   4. Click **Choose File** and then browse to the **f5-autoscale-bigip.template** file.
 
 <br>
 **AWS CLI**
 
 From the AWS CLI, use the following command syntax:
 ```
 aws cloudformation create-stack --stack-name Acme-autoscale-bigip --template-body file:///fullfilepath/f5-autoscale-bigip.template --parameters file:///fullfilepath/f5-autoscale-bigip-parameters.json --capabilities CAPABILITY_NAMED_IAM`
```
<br>
### Usage ###
Use this template to automate the auto scale implementation by providing the parameter values. You can use or change the default parameter values, which are defined in the AWS CloudFormation template on the AWS Console.  If using the AWS CLI, use the following JSON parameter file.


| Parameter | Required | Description |
| --- | --- | --- |
| deploymentName | x | Name the template uses to create object names |
| vpc | x | VPC where you want to deploy the BIG-IP VEs |
| availabilityZones | x | Availability Zones where you want to deploy BIG-IP VEs (we recommend at least 2) |
| subnets | x | Public or External Subnet for the Availability Zones |
| bigipSecurityGroup | x | AWS Security Group for BIG-IP VEs |
| bigipElasticLoadBalancer | x | AWS Elastic Load Balancer group for BIG-IPs |
| sshKey | x | EC2 KeyPair to enable SSH access to the BIG-IP instance |
| instanceType | x | AWS Instance Type (Default m3.2xlarge) |
| throughput | x | Maximum amount of throughput for BIG-IP VE (Default 1000Mbps) |
| adminUsername | x | BIG-IP Admin Username for clustering. Note that the user name can contain only alphanumeric characters, periods ( . ), underscores ( _ ), or hyphens ( - ). Note also that the user name cannot be any of the following: adm, apache, bin, daemon, guest, lp, mail, manager, mysql, named, nobody, ntp, operator, partition, password, pcap, postfix, radvd, root, rpc, rpm, sshd, syscheck, tomcat, uucp, or vcsa. |
| managementGuiPort | x | Port of BIG-IP management Configuration utility (Default 8443) |
| timezone | x | Olson timezone string from /usr/share/zoneinfo (Default UTC) |
| ntpServer | x | NTP server for this implementation (Default 0.pool.ntp.org) |
| scalingMinSize | x | Minimum number of BIG-IP instances (1-8) to be available in the AutoScale Group (Default 1) |
| scalingMaxSize | x | Maximum number of BIG-IP instances (2-8) that can be created in the AutoScale Group (Default 3) |
| scaleDownBytesThreshold | x | Incoming Bytes Threshold to begin scaling down BIG-IP Instances (Default 10000) |
| scaleUpBytesThreshold | x | Incoming Bytes Threshold to begin scaling up BIG-IP Instances (Default 35000) |
| notificationEmail |  | Valid email address to send Auto Scaling Event Notifications |
| virtualServicePort | x | Port on BIG-IP (Default 80) |
| applicationPort | x | Application Pool Member Port on BIG-IP (Default 80) |
| appInternalDnsName | x | DNS of the ELB used for the application, e.g. Acme.region.elb.amazonaws.com |
| policyLevel | x | WAF Policy Level to protect the application (Default high) |
| application |  | Application Tag (Default f5app) |
| environment |  | Environment Name Tag (Default f5env) |
| group |  | Group Tag (Default f5group) |
| owner |  | Owner Tag (Default f5owner) |
| costcenter |  | Costcenter Tag (Default f5costcenter) |
<br>




Example minimum **autoscale-bigip-parameters.json** using default values for unlisted parameters
```json
[
	{
		"ParameterKey":"deploymentName",
		"ParameterValue":"Acme"
	},
	{
		"ParameterKey":"vpc",
		"ParameterValue":"vpc-abcd1234"
	},
	{
		"ParameterKey":"availabilityZones",
		"ParameterValue":"us-east-1a,us-east-1b"
	},
	{
		"ParameterKey":"subnets",
		"ParameterValue":"subnet-abcd1234,subnet-abcd1234"
	},
	{
		"ParameterKey":"bigipSecurityGroup",
		"ParameterValue":"sg-abcd1234"
	},
	{
		"ParameterKey":"bigipElasticLoadBalancer",
		"ParameterValue":"Acme-BigipElb"
	},
	{
		"ParameterKey":"sshKey",
		"ParameterValue":"awskeypair"
	},
	{
		"ParameterKey":"notificationEmail",
		"ParameterValue":"user@company.com"
	},
	{
		"ParameterKey":"appInternalDnsName",
		"ParameterValue":"internal-Acme-AppElb-911355308.us-east-1.elb.amazonaws.com"
	},
	{
		"ParameterKey":"policyLevel",
		"ParameterValue":"high"
	}
]
```

## Configuration Example <a name="config"></a>

The following is a simple configuration diagram deployment. 

![Single NIC configuration example](images/config-diagram-autoscale-waf.png)

### Security blocking levels <a name="blocking"></a>
The security blocking level you choose when you configure the template determines how much traffic is blocked and alerted by the F5 WAF.

Attack signatures are rules that identify attacks on a web application and its components. The WAF has at least 2600 attack signatures available. The higher the security level you choose, the more traffic that is blocked by these signatures.

| Level | Details |
| --- | --- | --- |
| Low | The fewest attack signatures enabled. There is a greater chance of possible security violations making it through to the web applications, but a lesser chance of false positives. |
| Medium | A balance between logging too many violations and too many false positives. |
| High | The most attack signatures enabled. A large number of false positives may be recorded; you must correct these alerts for your application to function correctly. |

All traffic that is not being blocked is being used by the WAF for learning. Over time, if the WAF determines that traffic is safe, it allows it through to the application. Alternately, the WAF can determine that traffic is unsafe and block it from the application.

## Security Details <a name="securitydetail"></a>
This section has the entire code snippets for each of the lines you should ensure are present in your template file if you want to verify the integrity of the helper code in the template.

**/config/verifyHash section**

Note the hashed script-signature may be different in your template.<br>


```json
"/config/verifyHash": {
                "content": {
                  "Fn::Join": [
                    "\n",
                    [
                      "cli script /Common/verifyHash {",
                      "proc script::run {} {",
                      "        if {[catch {",
                      "            set hashes(f5-cloud-libs.tar.gz) a6a9db3b89bbd014413706f22fa619c3717fac41fc99ffe875589c90e9b85a05cea227c134ea6e5b519c8fee0d12f2175368e75917f31f447ece3d92f31814af",
                      "            set hashes(f5-cloud-libs-aws.tar.gz) 90058095cc536a057378a90ed19c3afe0cecd9034e1d1816745bd5ad837939623fad034ebd2ee9bdf594f33358b50c50f49a18c2ee7588ba89645142f2217330",
                      "            set hashes(asm-policy-linux.tar.gz) 63b5c2a51ca09c43bd89af3773bbab87c71a6e7f6ad9410b229b4e0a1c483d46f1a9fff39d9944041b02ee9260724027414de592e99f4c2475415323e18a72e0",
                      "            set hashes(f5.http.v1.2.0rc4.tmpl) 47c19a83ebfc7bd1e9e9c35f3424945ef8694aa437eedd17b6a387788d4db1396fefe445199b497064d76967b0d50238154190ca0bd73941298fc257df4dc034",
                      "            set hashes(f5.http.v1.2.0rc6.tmpl) 811b14bffaab5ed0365f0106bb5ce5e4ec22385655ea3ac04de2a39bd9944f51e3714619dae7ca43662c956b5212228858f0592672a2579d4a87769186e2cbfe",
                      "",
                      "            set file_path [lindex $tmsh::argv 1]",
                      "            set file_name [file tail $file_path]",
                      "",
                      "            if {![info exists hashes($file_name)]} {",
                      "                tmsh::log err \"No hash found for $file_name\"",
                      "                exit 1",
                      "            }",
                      "",
                      "            set expected_hash $hashes($file_name)",
                      "            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]",
                      "            if { $expected_hash eq $computed_hash } {",
                      "                exit 0",
                      "            }",
                      "            tmsh::log err \"Hash does not match for $file_path\"",
                      "            exit 1",
                      "        }]} {",
                      "            tmsh::log err {Unexpected error in verifyHash}",
                      "            exit 1",
                      "        }",
                      "    }",
                      "    script-signature OmyfJKVQkBj+Ks6SdIc2+UNxM2xFCK4MGizGysivShzeRof0EFlEUTQiZveZ4v2SElofUp5DMVKiTIIkM00kZ7LnwqvLYIOztDFNAtMGwO6/B/zA8jLhkfnA2xzxu9fFgFn3OEsc8QwbfFS1AqCMyyacbbiczJycHtu3z0a/8sqCgiZtcQ4iXqBP4fz+8HKLA36U0jpmW+z0gQQUwpiC+AfFWcAarXMtmpwLzScldnaZ5RLo0MG8EGrHmXiWjndSR/Ii9b3+vnHnceD6+sw7e7LXPvz+jV9/rFyEQOA1QNpv0Cy4SJcuY9NRjV9KNdBobJ5N+h2PZBlgaIdLMACAVQ==",
                      "}"
                    ]
                  ]
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
                      "if ! tmsh load sys config merge file /config/verifyHash; then",
                      "    echo cannot validate signature of /config/verifyHash",
                      "    exit",
                      "fi",
                      "echo loaded verifyHash",
                      "declare -a filesToVerify=(\"/config/cloud/f5-cloud-libs.tar.gz\" \"/config/cloud/f5-cloud-libs-aws.tar.gz\")",
                      "for fileToVerify in \"${filesToVerify[@]}\"",
                      "do",
                      "    echo verifying \"$fileToVerify\"",
                      "    if ! tmsh run cli script verifyHash \"$fileToVerify\"; then",
                      "        echo \"$fileToVerify\" is not valid",
                      "        exit 1",
                      "    fi",
                      "    echo verified \"$fileToVerify\"",
                      "done",
                      "mkdir -p /config/cloud/aws/node_modules",
                      "echo expanding f5-cloud-libs.tar.gz",
                      "tar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/aws/node_modules",
                      "tar xvfz /config/cloud/asm-policy-linux.tar.gz -C /config/cloud",
                      "cd /config/cloud/aws/node_modules/f5-cloud-libs",
                      "echo installing dependencies",
                      "npm install --production /config/cloud/f5-cloud-libs-aws.tar.gz",
                      "echo cloud libs install complete",
                      "touch /config/cloud/cloudLibsReady"
                    ]
                  ]
                },
                "mode": "000755",
                "owner": "root",
                "group": "root"
              }
```
