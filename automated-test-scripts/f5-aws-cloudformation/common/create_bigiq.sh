#!/usr/bin/env bash
#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

echo "license type: <LICENSE TYPE>"
bigiq_lic_pool="<BIGIQ LICENSE POOL>"
bigiq_lic_key="<AUTOFILL CLPV2 LICENSE KEY>"
case <LICENSE TYPE> in
bigiq)
    # Capture environment ids required to create stack
    vpc=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[] |select (.OutputKey=="Vpc")|.OutputValue')
    echo "VPC:$vpc"
    mgmt_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="managementSubnetAz1")|.OutputValue')
    echo "mgmt subnet az1:$mgmt_sub_az1"
    ext_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="subnet1Az1")|.OutputValue')
    echo "external subnet az1:$ext_sub_az1"
    # use published standalone big-iq template
    if [[ <REGION> == "us-east-1" ]]; then
        s3_prefix="s3."
    else
        s3_prefix="s3.<REGION>."
    fi
    if [[ <REGION> == "me-south-1" ]]; then
        instance_type="m5.2xlarge"
    else
        instance_type="m4.2xlarge"
    fi
    bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
    set_bigiq_pass="arn:aws:s3:::bigiqtest/passworddb.json"
    source_cidr=0.0.0.0/0
    aws cloudformation create-stack \
    --disable-rollback \
    --region <REGION> \
    --stack-name <STACK NAME>-bigiq \
    --tags Key=creator,Value=dewdrop Key=delete,Value=True \
    --template-url https://"$bucket_name".${s3_prefix}amazonaws.com/f5-existing-stack-byol-2nic-bigiq-licmgmt.template \
    --capabilities CAPABILITY_IAM \
    --parameters \
    ParameterKey=allowUsageAnalytics,ParameterValue=<ANALYTICS> \
    ParameterKey=Vpc,ParameterValue=$vpc \
    ParameterKey=instanceType,ParameterValue="$instance_type" \
    ParameterKey=restrictedSrcAddress,ParameterValue="$source_cidr" \
    ParameterKey=restrictedSrcAddressApp,ParameterValue="$source_cidr" \
    ParameterKey=sshKey,ParameterValue=<SSH KEY> \
    ParameterKey=managementSubnetAz1,ParameterValue=$mgmt_sub_az1 \
    ParameterKey=subnet1Az1,ParameterValue=$ext_sub_az1 \
    ParameterKey=ntpServer,ParameterValue=<NTP SERVER> \
    ParameterKey=timezone,ParameterValue=<TIMEZONE> \
    ParameterKey=bigIqPasswordS3Arn,ParameterValue=$set_bigiq_pass \
    ParameterKey=licenseKey1,ParameterValue=<AUTOFILL BIGIQ LICENSE KEY> \
    ParameterKey=regPoolKeys,ParameterValue=DO_NOT_CREATE \
    ParameterKey=licensePoolKeys,ParameterValue=$bigiq_lic_key
    echo "Creating BIGIQ using bigIQ standalone template for test" ;;
*)
    echo "BIG-IQ not required for test:StackId"  ;;
esac