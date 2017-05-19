#!/bin/bash

## Bash Script to deploy F5 template into AWS, using aws-cli/1.11.76 ##
<<<<<<< HEAD
## Example Command: ./deploy_2nic_ha_same-az.sh --licenseType Hourly --imageName Good200Mbps --instanceType t2.medium --bigipExternalSecurityGroup <value> --bigipManagementSecurityGroup <value> --sshKey <value> --managementSubnetAz1 <value> --subnet1Az1 <value> --vpc <value> --stackName <value>
=======
## Example Command: ./deploy_via_bash.sh --licenseType Hourly --imageName Good200Mbps --instanceType t2.medium --bigipExternalSecurityGroup <value> --bigipManagementSecurityGroup <value> --sshKey <value> --managementSubnetAz1 <value> --subnet1Az1 <value> --vpc <value> --stackName <value>
>>>>>>> 023a03d71f19b02cd5d8245eea508b8a495bdeac

# Assign Script Parameters and Define Variables 
# Specify static items, change these as needed or make them parameters
region="us-west-2"
restrictedSrcAddress="0.0.0.0/0"
tagValues='[{"Key": "application", "Value": "f5app"},{"Key": "environment", "Value": "f5env"},{"Key": "group", "Value": "f5group"},{"Key": "owner", "Value": "f5owner"},{"Key": "costcenter", "Value": "f5costcenter"}]'
<<<<<<< HEAD
ntpServer="0.pool.ntp.org"
timezone="UTC"
=======
>>>>>>> 023a03d71f19b02cd5d8245eea508b8a495bdeac

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
<<<<<<< HEAD
        -d|--licenseKey1)
            licenseKey1=$2
            shift 2;;
        -e|--licenseKey2)
            licenseKey2=$2
            shift 2;;
        -f|--bigipExternalSecurityGroup)
            bigipExternalSecurityGroup=$2
            shift 2;;
        -g|bigipManagementSecurityGroup)
            bigipManagementSecurityGroup=$2
            shift 2;;
        -h|--sshKey)
            sshKey=$2
            shift 2;;
        -i|--managementSubnetAz1)
            managementSubnetAz1=$2
            shift 2;;
        -j|--subnet1Az1)
            subnet1Az1=$2
            shift 2;;
        -k|--vpc)
            vpc=$2
            shift 2;;
        -l|--stackName)
=======
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
        -k|--subnet1Az1)
            subnet1Az1=$2
            shift 2;;
        -l|--vpc)
            vpc=$2
            shift 2;;
        -m|--stackName)
>>>>>>> 023a03d71f19b02cd5d8245eea508b8a495bdeac
            stackName=$2
            shift 2;;
        --)
            shift
            break;;
    esac
done

# If a required parameter is not passed, the script will prompt for it below 
required_variables="licenseType imageName instanceType bigipExternalSecurityGroup bigipManagementSecurityGroup sshKey managementSubnetAz1 subnet1Az1 vpc stackName "
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
    template="https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template"
fi 
# Prompt for license bandwidth if not supplied and Hourly is selected 
if [ $licenseType == "Hourly" ]
then 
    if [ -v $imageName ]
    then 
            read -p "Please enter value for imageName:" imageName
    fi
    template="https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-hourly-2nic-bigip.template"
fi

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as templates. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

# Deploy Template
if [ $licenseType == "BYOL" ]
then
<<<<<<< HEAD
    aws cloudformation create-stack --stack-name $stackName --template-url $template --capabilities CAPABILITY_IAM --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=bigipExternalSecurityGroup,ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=licenseKey2,ParameterValue=$licenseKey2 ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress ParameterKey=ntpServer,ParameterValue=$ntpServer ParameterKey=timezone,ParameterValue=$timezone --tags "$tagValues"
elif [ $licenseType == "Hourly" ]
then
    aws cloudformation create-stack --stack-name $stackName --template-url $template --capabilities CAPABILITY_IAM --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress ParameterKey=ntpServer,ParameterValue=$ntpServer ParameterKey=timezone,ParameterValue=$timezone --tags "$tagValues"
=======
    aws cloudformation create-stack --stack-name $stackName --template-url $template --capabilities CAPABILITY_IAM --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=bigipExternalSecurityGroup,ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=licenseKey1,ParameterValue=$licenseKey1 ParameterKey=licenseKey2,ParameterValue=$licenseKey2 ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress --tags "$tagValues"
elif [ $licenseType == "Hourly" ]
then
    aws cloudformation create-stack --stack-name $stackName --template-url $template --capabilities CAPABILITY_IAM --parameters ParameterKey=sshKey,ParameterValue=$sshKey ParameterKey=managementSubnetAz1,ParameterValue=$managementSubnetAz1 ParameterKey=bigipExternalSecurityGroup,ParameterValue=$bigipExternalSecurityGroup ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=bigipManagementSecurityGroup,ParameterValue=$bigipManagementSecurityGroup ParameterKey=subnet1Az1,ParameterValue=$subnet1Az1 ParameterKey=imageName,ParameterValue=$imageName ParameterKey=instanceType,ParameterValue=$instanceType ParameterKey=restrictedSrcAddress,ParameterValue=$restrictedSrcAddress --tags "$tagValues"
>>>>>>> 023a03d71f19b02cd5d8245eea508b8a495bdeac
else 
    echo "Uh oh, shouldn't make it here! Ensure license type is either Hourly or BYOL'"
    exit 1
fi
<<<<<<< HEAD
=======

# aws cloudformation create-stack --stack-name dadlani-ha-bash --template-url https://s3.amazonaws.com/f5-cft/f5-existing-stack-same-az-cluster-byol-2nic-bigip.template --capabilities CAPABILITY_IAM --parameters ParameterKey=sshKey,ParameterValue=dadlani-awskeypair ParameterKey=managementSubnetAz1,ParameterValue=subnet-56713831 ParameterKey=bigipExternalSecurityGroup,ParameterValue=sg-65df4b1e ParameterKey=Vpc,ParameterValue=vpc-800835e7 ParameterKey=licenseKey1,ParameterValue=NMMBD-UEZHT-BLFSQ-OBSAJ-WYSIVQQ ParameterKey=licenseKey2,ParameterValue=NMMBD-UEZHT-BLFSQ-OBSAJ-WYSIVQQ ParameterKey=bigipManagementSecurityGroup,ParameterValue=sg-b2c256c9 ParameterKey=subnet1Az1,ParameterValue=subnet-37703950 ParameterKey=imageName,ParameterValue=Good ParameterKey=instanceType,ParameterValue=t2.medium ParameterKey=restrictedSrcAddress,ParameterValue=0.0.0.0/0
>>>>>>> 023a03d71f19b02cd5d8245eea508b8a495bdeac
