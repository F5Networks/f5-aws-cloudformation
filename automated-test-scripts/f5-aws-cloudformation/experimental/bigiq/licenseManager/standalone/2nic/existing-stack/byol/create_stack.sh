#!/usr/bin/env bash
#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

#rm -f /tmp/<STACK NAME>
#curl -k <TEMPLATE URL> -o /tmp/<STACK NAME>
source_ip=`/usr/bin/curl ifconfig.co`
source_cidr=0.0.0.0/0
bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME> --template-url https://s3.amazonaws.com/"$bucket_name"/<TEMPLATE NAME> --capabilities CAPABILITY_IAM --parameters ParameterKey=allowUsageAnalytics,ParameterValue=<ANALYTICS> ParameterKey=Vpc,ParameterValue=<VPC> ParameterKey=instanceType,ParameterValue=<INSTANCE TYPE> ParameterKey=restrictedSrcAddress,ParameterValue="$source_cidr" ParameterKey=restrictedSrcAddressApp,ParameterValue="$source_cidr" ParameterKey=sshKey,ParameterValue=<SSH KEY> ParameterKey=subnet1Az1,ParameterValue=<SUBNET1 AZ1> ParameterKey=ntpServer,ParameterValue=<NTP SERVER> ParameterKey=timezone,ParameterValue=<TIMEZONE> ParameterKey=bigIqPasswordS3Arn,ParameterValue=<S3 ARN> <REG POOL KEYS PARAM> <NETWORK PARAM> <LICENSE PARAM> <LIC POOL KEYS>
