# f5-azure-arm-1nic

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Doc Status](http://readthedocs.org/projects/f5-sdk/badge/?version=latest)](https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-msft-azure-12-1-0.html)

## Introduction

This solution implements a Cloud Formation Template to deploy a base example of F5 in a two NIC deployment. In a two NIC implementation, interface #1 is for management and data-plane 
traffic from the Internet, and interface #2 is connected into the Amazon networks where traffic is processed by the pool members in a traditional two-ARM design. There are two templates, 
BYOL edition allows you to input an existing BIG-IP license, or hourly which utilizes pay as you go hourly billing. The “existing stack” cft incorporates existing Amazon Vpc. Check out 
our templates located in the “learning-stacks” folder if you would like to run a “full stack” which creates and configures Big-Ip, AWS Vpc,  as well as a backend Webserver.
## Documentation

Please see the project documentation - This is still being created

## Installation

You have 2 options for deploying this template:
  - Using the  Amazon Web Service deploy button
  - Using AWS Command Line Interface

### <a name="aws"></a>Amazon Web Services deploy button

Use this button to deploy the hourly template: 

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-Hourly&templateURL=https://s3-us-west-2.amazonaws.com/f5-dev/existing-stack-hourly-2nic-bigip.template" target="_blank">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/>
</a>

Use this button to deploy the BYOL template: 

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=BigIp-2nic-BYOL&templateURL=https://s3-us-west-2.amazonaws.com/f5-dev/existing-stack-byol-2nic-bigip.template" target="_blank">
    <img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/>
</a>

### <a name="powershell"></a>PowerShell

```powershell
    # Params below match to parameters in the azuredeploy.json that are gen-unique, otherwise pointing to
    # the azuredeploy.parameters.json file for default values.  Some options below are mandatory, some(such as deployment password for BIG IP)
<<<<<<< HEAD
    # can be supplied inline when running this script but if they arent then the default will be used as specificed in below param arguments
    # Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword yourpassword -dnsLabel f51nicdeploy01 -instanceName f51nic -licenseKey1 XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -resourceGroupName f51nicdeploy01 -EmailTo user@f5.com
=======
    # can be supplied inline when running this script but if they are not then the default will be used as specified in the param arguments
    # Example Command: .\Deploy_via_PS.ps1 -adminUsername azureuser -adminPassword yourpassword -dnsLabelPrefix f51nicdeploy01 -vmName f51nic -licenseToken XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -resourceGroupName f51nicdeploy01
>>>>>>> 9934511c811cb92072596a2cf05c8259c87c244f

    param(
    [Parameter(Mandatory=$True)]
    [string]
    $adminUsername,

    [Parameter(Mandatory=$True)]
    [string]
    $adminPassword,

    [Parameter(Mandatory=$True)]
    [string]
    $dnsLabel,

    [Parameter(Mandatory=$True)]
    [string]
    $instanceName,

    [string]
    $instanceType = "Standard_D2_v2",

    [string]
    $f5Sku = "Best",

    [Parameter(Mandatory=$True)]
    [string]
    $licenseKey1,

    [string]
    $restrictedSrcAddress  = "*",

    [Parameter(Mandatory=$True)]
    [string]
    $resourceGroupName,

    [string]
    $region = "West US",

    [string]
    $templateFilePath = "azuredeploy.json",

    [string]
    $parametersFilePath = "azuredeploy.parameters.json"
    )

    # Connect to Azure, right now it is only interactive login
    Login-AzureRmAccount

    # Create Resource Group for ARM Deployment
    New-AzureRmResourceGroup -Name $resourceGroupName -Location "$region"

    # Create Arm Deployment
    $pwd = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
    $deployment = New-AzureRmResourceGroupDeployment -Name $resourceGroupName -ResourceGroupName $resourceGroupName -TemplateFile $templateFilePath -TemplateParameterFile $parametersFilePath -Verbose -adminUsername "$adminUsername" -adminPassword $pwd -dnsLabel "$dnsLabel" -instanceName "$instanceName" -instanceType "$instanceType" -licenseKey1 "$licenseKey1" -restrictedSrcAddress "$restrictedSrcAddress" -f5Sku "$f5Sku"

    # Print Output of Deployment to Console
    $deployment
```


### <a name="cli"></a>Azure CLI(1.0) Usage
-----
```
    #!/bin/bash

    # Script to deploy 1nic/2nic ARM template into Azure, using azure cli 1.0
    # Example Command: ./deploy_via_bash.sh -u azureuser -p 'yourpassword' -d f51nicdeploy01 -n f52nic -l XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -r f51nicdeploy01 -y adminstrator@domain.com -z 'yourpassword'

    # Assign Script Paramters and Define Variables
    # Specify static items, change these as needed or make them parameters (instance_size is already an optional paramter)
    region="westus"
    template_file="azuredeploy.json"
    parameter_file="azuredeploy.parameters.json"
    instance_size="Standard_D2_v2"
    f5_sku="Best"

    while getopts u:p:d:n:s:l:r:y:z: option
    do	case "$option"  in
            u) admin_username=$OPTARG;;
            p) admin_password=$OPTARG;;
            d) dns_label=$OPTARG;;
            n) instance_name=$OPTARG;;
            s) instance_size=$OPTARG;;
            k) f5_sku=$OPTARG;;
            l) license_key_1=$OPTARG;;
            r) resource_group_name=$OPTARG;;
            y) azure_user=$OPTARG;;
            z) azure_pwd=$OPTARG;;
        esac
    done
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
<<<<<<< HEAD
    # such as can been done with Powershell...oh well!
<<<<<<< HEAD
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceSize\":{\"value\":\"$instance_size\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"f5Sku\":{\"value\":\"$f5_sku\"}}"
=======
    # such as can been done with PowerShell...oh well!
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabelPrefix\":{\"value\":\"$dns_label_prefix\"},\"vmName\":{\"value\":\"$vm_name\"},\"vmSize\":{\"value\":\"$vm_size\"},\"licenseToken1\":{\"value\":\"$license_token\"}}"
>>>>>>> 9934511c811cb92072596a2cf05c8259c87c244f
=======
    azure group deployment create -f $template_file -g $resource_group_name -n $resource_group_name -p "{\"adminUsername\":{\"value\":\"$admin_username\"},\"adminPassword\":{\"value\":\"$admin_password\"},\"dnsLabel\":{\"value\":\"$dns_label\"},\"instanceName\":{\"value\":\"$instance_name\"},\"instanceType\":{\"value\":\"$instance_size\"},\"licenseKey1\":{\"value\":\"$license_key_1\"},\"f5Sku\":{\"value\":\"$f5_sku\"}}"
>>>>>>> develop

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