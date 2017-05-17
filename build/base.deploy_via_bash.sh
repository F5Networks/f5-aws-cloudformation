#!/bin/bash

## Bash Script to deploy F5 template into AWS, using aws-cli/1.11.76 ##
# Example Command: <EXAMPLE_CMD>

# Assign Script Paramters and Define Variables
# Specify static items, change these as needed or make them parameters
region="us-west-2"
restrictedSrcAddress="0.0.0.0/0"
tagValues='[{"Key": "application", "Value": "f5app"},{"Key": "environment", "Value": "f5env"},{"Key": "group", "Value": "f5group"},{"Key": "owner", "Value": "f5owner"},{"Key": "costcenter", "Value": "f5costcenter"}]'

# Parse the command line arguments, primarily checking full params as short params are just placeholders
while [[ $# -gt 1 ]]
do
    case "$1" in
        <CASE_STATEMENTS>
    esac
done

#If a required parameter is not passed, the script will prompt for it below
required_variables=<REQUIRED_PARAMETERS>
for variable in $required_variables
        do
        if [ -z ${!variable} ] ; then
                read -p "Please enter value for $variable:" $variable
        fi
done

# Prompt for license key if not supplied and BYOL is selected 
if [ $licenseType == "BYOL" ]
then 
    <IF_LICENSE_NOT_ENTERED>
    
    template="<BYOL_TEMPLATE>"
fi 

# Prompt for license bandwidth if not supplied and Hourly is selected 
if [ $licenseType == "Hourly" ]
then 
    if [ -z $imageName ]
    then 
            read -p "Please enter value for imageName:" imageName
    fi
    template="<HOURLY_TEMPLATE>"
fi

echo "Disclaimer: Scripting to Deploy F5 Solution templates into Cloud Environments are provided as examples. They will be treated as best effort for issues that occur, feedback is encouraged."
sleep 3

# Deploy Template
if [ $licenseType == "BYOL" ]
then
    <DEPLOY_BYOL>

elif [ $licenseType == "Hourly" ]
then
    <DEPLOY_HOURLY>    
else 
    echo "Uh oh, shouldn't make it here! Ensure license type is either Hourly or BYOL'"
    exit 1
fi
