#!/bin/bash

## Bash Script to deploy an F5 ARM template into Azure, using azure cli 1.0 ##
<EXAMPLE_CMD>

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters
region="us-west-2"
restrictedSrcAddress="0.0.0.0/0"
tagValues='[{"Key": "application", "Value": "f5app"},{"Key": "environment", "Value": "f5env"},{"Key": "group", "Value": "f5group"},{"Key": "owner", "Value": "f5owner"},{"Key": "costcenter", "Value": "f5costcenter"}]'

# Parse the command line arguments, primarily checking full params as short params are just placeholders
while [[ $# -gt 1 ]]
do
    case "$1" in
        -a|--licenseType)
            licenseType=$2
            shift 2;;<LICENSE_PARAMETERS><DYNAMIC_PARAMETERS>
        -b|--imageName)
            azureLoginUser=$2
            shift 2;;
        -c|--instanceType)
            azureLoginPassword=$2
            shift 2;;
        -d|--restrictedSrcAddress)
            licenseType=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

#If a required parameter is not passed, the script will prompt for it below
required_variables="<REQUIRED_PARAMETERS>"
for variable in $required_variables
        do
        if [ -z ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

<LICENSE_CHECK>

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

# Deploy Template
<DEPLOYMENT_CREATE>