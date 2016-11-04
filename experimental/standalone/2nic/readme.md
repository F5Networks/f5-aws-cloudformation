# Deploying the BIG-IP in AWS - 2 NIC

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Doc Status](http://readthedocs.org/projects/f5-sdk/badge/?version=latest)](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-multi-nic-setup-amazon-ec2-12-1-0.html)

## Introduction

This solution implements a Cloud Formation Template to deploy a base example of F5 in a two NIC deployment. In a two NIC implementation, interface #1 is for management and data-plane traffic from the Internet, and interface #2 is connected into the Amazon networks where traffic is processed by the pool members in a traditional two-ARM design. 

This solution provides two different template options:
  - **BYOL**<br>
  The BYOL (bring your own license) template allows you to input an existing BIG-IP license.
  - **Hourly**<br>
  The Hourly template which uses pay-as-you-go hourly billing
  
  The **existing stack** CloudFormation template incorporates an existing Virtual Private Cloud (VPC). If you would like to run a *full stack* which creates and configures the BIG-IP, the AWS infrastructure, as well as a backend webserver, see the templates located in the **learning-stacks** folder.
  
## Documentation

Please see the project documentation - This is still being created

## Installation

You have two options for deploying this template: 
  - Using the AWS deploy buttons 
  - Using [CLI Tools](#cli)

### Using the AWS deploy buttons
The easiest way to deploy of the of CloudFormation templates is to use the appropriate Launch button.
<br>
<br>

**Hourly deploy button**

Use this button to deploy the **hourly** template: 

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-Hourly&templateURL=https://s3-us-west-2.amazonaws.com/f5-dev/existing-stack-hourly-2nic-bigip.template">
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
| webserverPrivateIp | x | Web Server IP used for the BIG-IP pool member |

<br>
<br>

  **BYOL deploy button**

Use this button to deploy the **BYOL** template: 

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BYOL&templateURL=https://s3-us-west-2.amazonaws.com/f5-dev/existing-stack-byol-2nic-bigip.template">
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
| webserverPrivateIp | x | Web Server IP used for the BIG-IP pool member |


### <a name="cli"></a>AWS CLI Usage
-----
   #!/bin/bash

    # Script to deploy 1nic/2nic ARM template into Azure, using azure cli 1.0
    # Example Command: ./deploy_via_bash.sh -u awsuser -p 'yourpassword' -n f52nic -l XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -y admin -z 'yourpassword'

    # Assign Script Paramters and Define Variables
    # Specify static items, change these as needed or make them parameters (instance_size is already an optional paramter)

    while getopts az:esg:i:k:msg:maz1:n:p:r:s:s1:u:v:w: option
    do case "$option" in
            az) az=$OPTARG;;
            esg) external_security_group=$OPTARG;;
            i) license_type=$OPTARG;;
            k) key_name=$OPTARG;;
            msg) management_security_group=$OPTARG;;
            maz1) managment_subnet_az1=$OPTARG;;
            n) stack_name=$OPTARG;;
            p) admin_password=$OPTARG;;
            r) resource_group_name=$OPTARG;;
            s) instance_type=$OPTARG;;
            s1) subnet1_az1=$OPTARG;;
            u) admin_username=$OPTARG;;
            v) vpc=$OPTARG;;
            w) webserver_private_ip=$OPTARG;;
        esac
    done
    echo $
    # Check for Mandatory Args
    if [ ! "$admin_username" ] || [ ! "$admin_password" ] || [ ! "$dns_label" ] || [ ! "$instance_name" ] || [ ! "$license_token" ] || [ ! "$resource_group_name" ] || [ ! "$azure_user" ] || [ ! "$azure_pwd" ]
    then
        echo "One of the mandatory parameters was not specified!"
        exit 1
    fi


    # Login to Azure, for simplicity in this example using username and password as supplied as script arguments y and z
    azure login -u $azure_user -p $azure_pwd

    # Switch to ARM mode
    azure config mode arm

    # Create ARM Group
    azure group create -n $resource_group_name -l $region

    # Deploy ARM Template, right now cannot specify parameter file AND parameters inline via Azure CLI,
    # such as can been done with Powershell...oh well!
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceSize\":{\"value\":\"$instance_size\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"f5Sku\":{\"value\":\"$f5_sku\"}}"
=======
    # such as can been done with PowerShell...oh well!
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabelPrefix\":{\"value\":\"$dns_label_prefix\"},\"vmName\":{\"value\":\"$vm_name\"},\"vmSize\":{\"value\":\"$vm_size\"},\"licenseToken1\":{\"value\":\"$license_token\"}}"
=======
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceType\":{\"value\":\"$instance_size\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"f5Sku\":{\"value\":\"$f5_sku\"}}"
echo "Downloading latest CFT from github....$cft"
curl -sSk -o $cft --max-time 15 https://gitswarm.f5net.com/cloudsolutions/f5-aws-cloudformation/raw/develop/experimental/$folder$cft
echo "Done."
# Create Stack
echo "Creating stack with name $stackname"
stackcreate=$(aws cloudformation create-stack --region us-east-1 --template-body file://$cft --stack-name $stackname --parameters $parms 2>&1)
echo "Stack initiated: $stackcreate"
stackexist=$(echo $stackcreate | grep exists)
if [ -z "$stackexist" ]
 then
 echo "Waiting 120 seconds for VPC resources to be built in aws......\n"
 sleep 120
fi
echo "Locating VPC information"

# Locate BIG-IP Managment Addresses
bigip1=$(aws cloudformation describe-stack-resources --stack-name $stackname --logical-resource-id $bigip_resource_id | grep PhysicalResourceId | sed -e "s/\(\"P\).*\(:\)//" | sed -e "s/[\", ]//g")
echo "Bigip1 Management IP Address: $bigip1"
bigip2=$(aws cloudformation describe-stack-resources --stack-name $stackname --logical-resource-id $bigip2_resource_id | grep PhysicalResourceId | sed -e "s/\(\"P\).*\(:\)//" | sed -e "s/[\", ]//g")
echo "Bigip2 Management IP Address: $bigip2"

# Locate EIP assigned to applicaiton
eip=$(aws cloudformation describe-stack-resources --stack-name $stackname --logical-resource-id $eip_resource_id | grep PhysicalResourceId | sed -e "s/\(\"P\).*\(:\)//" | sed -e "s/[\", ]//g")
echo "Application EIP IP Address: $eip"

# Locate which bigip ownes EIP
owneip=$(aws ec2 describe-addresses --filter Name="public-ip",Values="$eip" | grep PrivateIpAddress | sed -e "s/\(\"P\).*\(:\)//" | sed -e "s/[\", ]//g")
echo "EIP is currently assigned to: $owneip"

# Locate security group GroupId
if [ $answer = 5 ] || [ $answer = 6 ]
 then
  groupid=$(aws ec2 describe-security-groups --filters Name=group-name,Values=*${stackname}-bigipExternalSecurityGroup* | grep GroupId | sed -e "s/\(\"G\).*\(:\)//" | sed -e "s/[\", ]//g")
  echo "Security GroupId: $groupid \n"
  echo "Use the following aws command to cause HA failure:\naws ec2 revoke-security-group-ingress --group-id $groupid --protocol udp --port 1026 --cidr 10.0.0.0/16 \n"
  echo "Use the following aws command to restore HA:\naws ec2 authorize-security-group-ingress --group-id $groupid --protocol udp --port 1026 --cidr 10.0.0.0/16 \n"
fi
if [ -z "$stackexist" ]
 then
 echo "Big-ip's will be ready to log into in 15 minutes."
fi
 bigip1_id=$(aws cloudformation describe-stack-resources --stack-name $stackname --logical-resource-id Bigip1Instance | grep PhysicalResourceId | sed -e "s/\(\"P\).*\(:\)//" | sed -e "s/[\", ]//g")
 echo "Checking to see if BIG-IP1 (${bigip1_id}) is up"
x=0
echo "Verifying bigip1 status, this could take several minutes...."
while [ $x -lt 16 ]; do
    bigip1_up=$(aws ec2 describe-instance-status --instance-id $bigip1_id --filters Name=instance-state-name,Values=running Name=instance-status.reachability,Values=passed | grep "Code")
    if [ $x -eq 16 ]; then
       echo "bigip1 not up yet after 15 minutes, giving up"
    fi   
    if [ -n "$bigip1_up" ]; then     
        echo -n "bigip1 ($bigip1_id)is up with "
        echo -n $bigip1_up | grep Code
        x=20
        
    else
        echo -n "$((x = $x +1))," 
        sleep 60
    fi
done
y=0
echo "Checking to see if website is up...."
while [ $y -lt 16 ]; do
    app_up=$(curl -vs -o /dev/null http://$eip 2>&1 | grep "OK")
    if [ -z $app_up ]; then
    echo -n "$((y = $y +1)),"
    sleep 60
    else
    echo "$app_up"
    y=16
    fi
done
 
echo "Don't forget to delete your stack when you are finished!:\n\naws cloudformation delete-stack --stack-name $stackname\n"
echo "---end $0 script---" 


```

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

## Unit Tests

Simply deploying the ARM template and completing use case fulfills a functional test



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