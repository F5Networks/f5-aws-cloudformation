#!/bin/bash

## Bash Script to deploy NIC template into AWS, using aws-cli/1.11.76 ##
## Example Command: ./deploy_via_bash.sh --licenseType Hourly --imageName Good200Mbps --instanceType t2.medium --bigipExternalSecurityGroup <value> --sshKey <value> --subnet1Az1 <value> --vpc <value> --stackName <value>

# Assign Script Parameters and Define Variables 
# Specify static items, change these as needed or make them parameters
region="us-west-2"
restrictedSrcAddress="0.0.0.0/0"
tagValues='[{"Key": "application", "Value": "f5app"},{"Key": "environment", "Value": "f5env"},{"Key": "group", "Value": "f5group"},{"Key": "owner", "Value": "f5owner"},{"Key": "costcenter", "Value": "f5costcenter"}]'

# Parse the command line arguments, and set parameters.
while [[ $# -gt 1 ]]
do
    case "$1" in
        -a|--licenseType)
            licenseType=$2
            shift 2;;
        -b|--imageName)
            imageName=$2
            shift 2;;
        -c|--instanceType)
            instanceType=$2
            shift 2;;
        -d|--restrictedSrcAddress)
            restrictedSrcAddress=$2
            shift 2;;
        -e|--licenseKey1)
            licenseKey1=$2
            shift 2;;
        -f|--bigipExternalSecurityGroup)
            bigipExternalSecurityGroup=$2
            shift 2;;
        -g|--sshKey)
            sshKey=$2
            shift 2;;
        -h|--subnet1Az1)
            subnet1Az1=$2
            shift 2;;
        -i|--vpc)
            vpc=$2
            shift 2;;
        -j|--stackName)
            stackName=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

# If a required parameter is not passed, the script will prompt for it below 
required_variables="licenseType imageName instanceType bigipExternalSecurityGroup sshKey subnet1Az1 vpc stackName "
for variable in $required_variables
do
    if [ -z ${!variable} ]
    then
            read -p "Please enter value for $variable:" $variable
    fi 
done

# Prompt for license key if not supplied and BYOL is selected 
if [ $licenseType == "BYOL" ]
then 
    if [ -z $licenseKey1 ]
    then
            read -p "Please enter value for licenseKey1:" licenseKey1
    fi
    template="https://s3.amazonaws.com/f5-cft/f5-existing-stack-byol-1nic-bigip.template"
fi 
# Prompt for license bandwidth if not supplied and Hourly is selected 
if [ $licenseType == "Hourly" ]
then 
    if [ -z $imageName ]
    then 
            read -p "Please enter value for imageName:" imageName
    fi
    template="https://s3.amazonaws.com/f5-cft/f5-existing-stack-hourly-1nic-bigip.template"
fi

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as templates. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

# Deploy Template
if [ $licenseType == "BYOL" ]
then
    aws cloudformation create-stack --stack-name $stackName --template-url $template --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress --tags "$tagValues"
elif [ $licenseType == "Hourly" ]
then
    aws cloudformation create-stack --stack-name $stackName --template-url $template --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress --tags "$tagValues"
else 
    echo "Uh oh, shouldn't make it here! Ensure license type is either Hourly or BYOL'"
    exit 1
fi
