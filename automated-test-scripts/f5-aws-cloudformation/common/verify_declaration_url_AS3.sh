#!/usr/bin/env bash
#  expectValue = "SUCCESS"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 50

# locate bigip ip addresses: used for all tests
case <SOLUTION TYPE> in
autoscale)
  bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
  instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup | jq -r '.AutoScalingGroups[].Instances[] |select (.ProtectedFromScaleIn==true) |.InstanceId')
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    IP=$(aws ec2 describe-instances --instance-ids $instanceId --region <REGION> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
    echo "Bigip1Url=$IP"
  else # Get the private IP address
    IP=$(aws ec2 describe-instances --instance-ids $instanceId --region <REGION> --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)
    echo "Bigip1Url=$IP"
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion"
  fi;;
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
standalone)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    IP=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "Bigip1Url=$IP"
  else
    instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
    echo "instanceId=$instanceId"
    IP=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[0].PrivateIpAddress')
    echo "Bigip1Private=$IP"
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion"
  fi ;;
*)
  echo "No Matching type"
  exit 1 ;;
esac

# test for empty variables and set number of bigips
if [[ -n "$IP" && -n "$IP2" ]]; then
  number_bigips=2
  echo "Number of bigips is equal to:$number_bigips"
elif [ -n "$IP" ]; then
  number_bigips=1
  echo "Number of bigips is equal to:$number_bigips"
else
  echo "Error, number of bigip addressess gathered incorrect:$IP,$IP2"
  exit 1
fi

# grab url definition when using url to define declaration and sort
case <DECLARATION URL> in
none)
 ;;
default)
 ;;
*)
  echo "Grabbing url defined declaration"
  decl_response=$(curl -sk <DECLARATION URL> |jq -S .)
  echo "Url Declaration: $decl_response" ;;
esac

# grab declarations from big-ips, sort, and remove timestamp
case $number_bigips in
1)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    as3_response=$(curl -sku <CUSTOM USER>:'<AUTOFILL PASSWORD>' https://${IP}:<MGMT PORT>/mgmt/shared/appsvcs/declare |jq -S 'del(.controls, .archiveTimestamp)')
  else
    jq_install=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} 'sudo apt-get install -y jq')
    echo "JQ Install: $jq_install"
    as3_response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} "curl -sku <CUSTOM USER>:'<AUTOFILL PASSWORD>' https://${IP}:<MGMT PORT>/mgmt/shared/appsvcs/declare |jq -S 'del(.controls, .archiveTimestamp)'")
  fi
  echo "AS3 Declaration: $as3_response" ;;
2)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    as3_response=$(curl -sku <CUSTOM USER>:'<AUTOFILL PASSWORD>' https://${IP}:<MGMT PORT>/mgmt/shared/appsvcs/declare |jq -S 'del(.controls, .archiveTimestamp)')
  else
    jq_install=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} 'sudo apt-get install -y jq')
    echo "JQ Install: $jq_install"
    as3_response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} "curl -sku <CUSTOM USER>:'<AUTOFILL PASSWORD>' https://${IP}:<MGMT PORT>/mgmt/shared/appsvcs/declare |jq -S 'del(.controls, .archiveTimestamp)'")
  fi
  echo "AS3 Declaration: $as3_response" ;;
*)
  echo "Number of bigips incorrect:$number_bigips"
  exit 1 ;;
esac

# Evaluate
# none test case
if [[ "<DECLARATION URL>" == "none" ]]; then
    echo "No AS3 declaration installed"
    result="SUCCESS"
# default test cases
elif [[ "<DECLARATION URL>" == "default" ]]; then
    echo "Evaluate big-ip for default as3 declaration"
    if [[ -n "$as3_response" ]]; then
        result="SUCCESS"
    else
        result="FAILED"
    fi
# url test cases
else
    echo "Evaluate big-ip for as3 url supplied declaration"
    if [[ "$as3_response" == "$decl_response" ]]; then
        result="SUCCESS"
    else
        result="FAILED"
    fi
fi
echo "$result"
