#!/bin/bash

## Bash Script to deploy F5 template into AWS, using aws-cli/1.11.165 ##
# Example Command: ./deploy_via_bash.sh --stackName <value> --licenseType Hourly --sshKey <value> --managementSubnetAz1 <value> --subnet1Az1 <value> --imageName Good200Mbps --restrictedSrcAddressApp <value> --Vpc <value> --instanceType t2.medium --restrictedSrcAddress <value>

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters
region="us-west-2"
restrictedSrcAddress="0.0.0.0/0"
tagValues='[{"Key": "application", "Value": "f5app"},{"Key": "environment", "Value": "f5env"},{"Key": "group", "Value": "f5group"},{"Key": "owner", "Value": "f5owner"},{"Key": "costcenter", "Value": "f5costcenter"}]'
ntpServer="0.pool.ntp.org"
timezone="UTC"

# Parse the command line arguments, primarily checking full params as short params are just placeholders
while [[ $# -gt 1 ]]
do
    case "$1" in
        --licenseKey1)
			licenseKey1=$2
			shift 2;;
		--licenseType)
			licenseType=$2
			shift 2;;
		--sshKey)
			sshKey=$2
			shift 2;;
		--managementSubnetAz1)
			managementSubnetAz1=$2
			shift 2;;
		--subnet1Az1)
			subnet1Az1=$2
			shift 2;;
		--stackName)
			stackName=$2
			shift 2;;
		--imageName)
			imageName=$2
			shift 2;;
		--restrictedSrcAddressApp)
			restrictedSrcAddressApp=$2
			shift 2;;
		--Vpc)
			Vpc=$2
			shift 2;;
		--instanceType)
			instanceType=$2
			shift 2;;
		--restrictedSrcAddress)
			restrictedSrcAddress=$2
			shift 2;;
		
        --)
			shift
			break;;
    esac
done

#If a required parameter is not passed, the script will prompt for it below
required_variables="stackName licenseType sshKey managementSubnetAz1 subnet1Az1 imageName restrictedSrcAddressApp Vpc instanceType restrictedSrcAddress "
for variable in $required_variables
do
    while [ -z ${!variable} ]
    do
        read -p "Please enter value for $variable:" $variable
    done
done

# Prompt for license key if not supplied and BYOL is selected 
if [ $licenseType == "BYOL" ]
then 
    while [ -z $licenseKey1 ]
    do
        read -p "Please enter value for licenseKey1:" licenseKey1
    done
    while [ -z $licenseKey2 ]
    do
        read -p "Please enter value for licenseKey2:" licenseKey2
    done
    
    template="https://f5-cft.s3.amazonaws.com/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template"
fi 

# Prompt for license bandwidth if not supplied and Hourly is selected 
if [ $licenseType == "Hourly" ]
then 
    while [ -z $imageName ]
    do 
        read -p "Please enter value for imageName:" imageName
    done
    
    template="https://f5-cft.s3.amazonaws.com/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template"
fi

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

# Deploy Template
if [ $licenseType == "BYOL" ]
then
    aws cloudformation create-stack --stack-name $stackName --template-url $template --capabilities CAPABILITY_IAM --parameters ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=restrictedSrcAddressApp,ParameterValue=$restrictedSrcAddressApp ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress ParameterKey=ntpServer,ParameterValue=$ntpServer ParameterKey=timezone,ParameterValue=$timezone --tags "$tagValues"

elif [ $licenseType == "Hourly" ]
then
    aws cloudformation create-stack --stack-name $stackName --template-url $template --capabilities CAPABILITY_IAM --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=restrictedSrcAddressApp,ParameterValue=$restrictedSrcAddressApp ParameterKey=Vpc,ParameterValue=$Vpc ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress ParameterKey=ntpServer,ParameterValue=$ntpServer ParameterKey=timezone,ParameterValue=$timezone --tags "$tagValues"
else 
    echo "This failure may have been caused by an error in license type: Please ensure license type is either Hourly or BYOL'"
    exit 1
fi
