#!/usr/bin/env bash
#  expectValue = "SUCCESS"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 50

# locate bigip ip addresses: used for all tests
case <SOLUTION TYPE> in
ha)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    IP=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "Bigip1Url=$IP"
    IP2=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "Bigip2Url=$IP2"
  else
    instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
    echo "instanceId=$instanceId"
    IP=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[0].PrivateIpAddress')
    echo "Bigip1Private=$IP"
    instanceId2=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2InstanceId")|.OutputValue')
    echo "instanceId=$instanceId2"
    IP2=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId2|jq -r '.Reservations[0].Instances[0].PrivateIpAddress')
    echo "Bigip1Private=$IP2"
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion"
  fi ;;
*)
  echo "No Matching type"
  exit 1 ;;
esac


# grab declarations from big-ips, sort, and remove timestamp

if [[ "<PUBLIC IP>" == "Yes" ]]; then
  cfe_response=$(curl -sku <CUSTOM USER>:'<AUTOFILL PASSWORD>' https://${IP}:<MGMT PORT>/mgmt/shared/cloud-failover/declare |jq -S)
else
  cfe_response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} "curl -sku <CUSTOM USER>:'<AUTOFILL PASSWORD>' https://${IP}:<MGMT PORT>/mgmt/shared/cloud-failover/declare |jq .")
fi
echo "CFE Declaration: $cfe_response"

# Evaluate
if echo $cfe_response | jq -r .message | grep 'success'; then
    result="SUCCESS"
else
    result="FAILED"
fi
echo "$result"