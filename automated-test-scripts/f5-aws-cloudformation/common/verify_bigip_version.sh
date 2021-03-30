#!/usr/bin/env bash
#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

# locate bigip ip addresses: used for all tests
case <SOLUTION TYPE> in
autoscale)
  bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
  instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
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

# list ntp settings
case $number_bigips in
1)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh list sys software')
  else
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh list sys software')
  fi
  echo "Response: $response"  ;;
2)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh list sys software')
    response2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP2} 'tmsh list sys software')
  else
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh list sys software')
    response2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP2" 'tmsh list sys software')
  fi
  echo "Response: $response"
  echo "Response: $response2" ;;
esac

# evaluate response
if [[ "$number_bigips" = 1 ]]; then
  if echo $response | grep '<BIG-IP VERSION>' && echo $response | grep '<BIG-IP BUILD>'; then
    echo "Response: $response"
    echo "SUCCESS"
  else
    echo "Response: $response"
    echo "FAILED"
  fi
elif [[ "$number_bigips" = 2 ]]; then
  if echo $response | grep '<BIG-IP VERSION>' && echo $response | grep '<BIG-IP BUILD>' && echo $response2 | grep '<BIG-IP VERSION>' && echo $response2 | grep '<BIG-IP BUILD>'; then
    echo "Response: $response"
    echo "Response2: $response2"
    echo "SUCCESS"
  else
    echo "Response: $response"
    echo "Response2: $response2"
    echo "FAILED"
  fi
fi
