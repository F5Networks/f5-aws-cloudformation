#!/bin/bash

## Bash Script to deploy F5 1 NIC template into AWS, using aws-cli/1.11.76 ##
## Example Command: ./deploy_2nic_ha.sh --licenseType BYOL --imageName Good200Mbps --instanceType t2.medium --licenseKey1 <value> --licenseKey2 <value> --bigipExternalSecurityGroup <value> --bigipManagementSecurityGroup <value> --sshKey <value> --managementSubnetAz1 <value> --managementSubnetAz2 <value> --subnet1Az1 <value> --subnet1Az2 <value> --vpc <value> --stackName <value>

# Assign Script Parameters and Define Variables 
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
        -f|--licenseKey2)
            licenseKey2=$2
            shift 2;;
        -g|--bigipExternalSecurityGroup)
            bigipExternalSecurityGroup=$2
            shift 2;;
        -h|bigipManagementSecurityGroup)
            bigipManagementSecurityGroup=$2
            shift 2;;
        -i|--sshKey)
            sshKey=$2
            shift 2;;
        -j|--managementSubnetAz1)
            managementSubnetAz1=$2
            shift 2;;
        -k|--managementSubnetAz2)
            managementSubnetAz2=$2
            shift 2;;
        -l|--subnet1Az1)
            subnet1Az1=$2
            shift 2;;
        -m|--subnet1Az2)
            subnet1Az2=$2
            shift 2;;
        -n|--vpc)
            vpc=$2
            shift 2;;
        -o|--stackName)
            stackName=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

# If a required parameter is not passed, the script will prompt for it below 
required_variables="licenseType imageName instanceType bigipExternalSecurityGroup bigipManagementSecurityGroup sshKey managementSubnetAz1 managementSubnetAz2 subnet1Az1 subnet1Az2 vpc stackName "
for variable in $required_variables
do
    if [ -v ${!variable} ]
    then
            read -p "Please enter value for $variable:" $variable
    fi 
done

# Prompt for license key if not supplied and BYOL is selected 
# TODO: maybe do something like if numkeys < 2 loop twice to get two license keys. 
if [ $licenseType == "BYOL" ]
then 
    if [ -v $licenseKey1 ]
    then
            read -p "Please enter value for licenseKey1:" licenseKey1
    fi
    if [ -v $licenseKey2 ]
    then
            read -p "Please enter value for licenseKey2:" licenseKey2
    fi
    template="https://s3.amazonaws.com/f5-cft/f5-existing-stack-across-az-cluster-byol-2nic-bigip.template"
fi 
# Prompt for license bandwidth if not supplied and Hourly is selected 
if [ $licenseType == "Hourly" ]
then 
    if [ -v $imageName ]
    then 
            read -p "Please enter value for imageName:" imageName
    fi
    template="https://s3.amazonaws.com/f5-cft/f5-existing-stack-across-az-cluster-hourly-2nic-bigip.template"
fi

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as templates. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

# Deploy Template
if [ $licenseType == "BYOL" ]
then
    aws cloudformation create-stack --stack-name $stackName --template-url $template --capabilities CAPABILITY_IAM --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=managementSubnetAz2,ParameterValue=$managementSubnetAz2 ParameterKey=bigipExternalSecurityGroup,ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=licenseKey2,ParameterValue=$licenseKey2 ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=subnet1Az2,ParameterValue=$subnet1Az2 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress --tags "$tagValues"
elif [ $licenseType == "Hourly" ]
then
    aws cloudformation create-stack --stack-name $stackName --template-url $template --capabilities CAPABILITY_IAM --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=managementSubnetAz2,ParameterValue=$managementSubnetAz2 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=subnet1Az2,ParameterValue=$subnet1Az2 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress --tags "$tagValues"
else
    echo "Uh oh, shouldn't make it here! Ensure license type is either Hourly or BYOL'"
    exit 1
fi