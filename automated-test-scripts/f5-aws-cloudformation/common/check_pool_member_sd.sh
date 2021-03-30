#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 10

# locate bigip ip addresses: used for all tests
case <SOLUTION TYPE> in
autoscale)
  bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
  instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
  IP=$(aws ec2 describe-instances --instance-ids $instanceId --region <REGION> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
  echo "Bigip1Url=$IP" ;;
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

# grab instance ID of the demo webserver server
demo_instanceid=$(aws cloudformation list-stack-resources --stack-name <STACK NAME>-vpc --region <REGION> |jq -r '.StackResourceSummaries[]| select(.LogicalResourceId=="Webserver")| .PhysicalResourceId')

#Get Dewpoint server IP address - Pool member address
demo_private_ip=$(aws ec2 describe-instances --region <REGION> --instance-id $demo_instanceid --query "Reservations[*].Instances[*].PrivateIpAddress" --output text)

# grab configured pools on big-ips
case $number_bigips in
1)
  ssh-keygen -R $IP 2>/dev/null
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    response=$(curl -k -u <CUSTOM USER>:'<AUTOFILL PASSWORD>' -H "Content-Type: application/json" https://$IP:<MGMT PORT>/mgmt/tm/ltm/pool/AWS-SD-App.app~AWS-SD-App_pool/members | jq .items[].address)
  else
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} "curl -k -u <CUSTOM USER>:'<AUTOFILL PASSWORD>' -H "Content-Type: application/json" https://$IP:<MGMT PORT>/mgmt/tm/ltm/pool/AWS-SD-App.app~AWS-SD-App_pool/members | jq .items[].address")
  fi
  echo "response: $response" ;;
2)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    response=$(curl -k -u <CUSTOM USER>:'<AUTOFILL PASSWORD>' -H "Content-Type: application/json" https://$IP:<MGMT PORT>/mgmt/tm/ltm/pool/AWS-SD-App.app~AWS-SD-App_pool/members | jq .items[].address)
    response2=$(curl -k -u <CUSTOM USER>:'<AUTOFILL PASSWORD>' -H "Content-Type: application/json" https://$IP2:<MGMT PORT>/mgmt/tm/ltm/pool/AWS-SD-App.app~AWS-SD-App_pool/members | jq .items[].address)
  else
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} "curl -k -u <CUSTOM USER>:'<AUTOFILL PASSWORD>' -H "Content-Type: application/json" https://$IP:<MGMT PORT>/mgmt/tm/ltm/pool/AWS-SD-App.app~AWS-SD-App_pool/members | jq .items[].address")
    response2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} "curl -k -u <CUSTOM USER>:'<AUTOFILL PASSWORD>' -H "Content-Type: application/json" https://$IP2:<MGMT PORT>/mgmt/tm/ltm/pool/AWS-SD-App.app~AWS-SD-App_pool/members | jq .items[].address")
  fi
  echo "response: $response"
  echo "response: $response2" ;;
esac

# evaluate response
if [[ "$number_bigips" = 1 ]]; then
  if echo $response | grep "$demo_private_ip"; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi
elif [[ "$number_bigips" = 2 ]]; then
  if echo $response | grep "$demo_private_ip" && echo $response2 | grep "$demo_private_ip"; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi
fi
