#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10

if [[ "<PUBLIC IP>" == "Yes" ]]; then
  IP=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
  echo "Bigip1Url=$IP"
  instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
  echo "instanceId=$instanceId"
  IP2=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2Url")|.OutputValue|split(":")[1]|.[2:]')
  echo "Bigip2Url=$IP2"
  instanceId2=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2InstanceId")|.OutputValue')
  echo "instanceId=$instanceId2"
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
fi

if [[ "<PUBLIC IP>" == "Yes" ]]; then
  state=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh show sys failover')
  state2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP2} 'tmsh show sys failover')
else
  state=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh show sys failover')
  state2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP2" 'tmsh show sys failover')
fi
echo "State: $state"
echo "State2: $state2"
echo "Getting table route association for 192.0.2.0/24"
table_target_route=$(aws ec2 describe-route-tables --region <REGION> | jq -r '.RouteTables[] | select (.Tags[].Value=="External Route Table<STACK NAME>-vpc")|.Routes[] | select (.DestinationCidrBlock=="192.0.2.0/24") | .InstanceId')
echo "Table target route: $table_target_route"

if echo $state | grep 'active'; then
    if [[ "$instanceId" == "$table_target_route" ]]; then
        result="SUCCESS"
    else
        result="FAILED"
    fi
elif echo $state2 | grep 'active'; then
    if [[ "$instanceId2" == "$table_target_route" ]]; then
        result="SUCCESS"
    else
        result="FAILED"
    fi
fi

echo "$result"