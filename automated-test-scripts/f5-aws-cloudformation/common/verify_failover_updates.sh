#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10
#  expectFailValue = "FAILED"


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
fi


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

if [[ "<PUBLIC IP>" == "Yes" ]]; then
  state=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh show sys failover')
  state2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP2} 'tmsh show sys failover')
  echo "State: $state"
  echo "State2: $state2"
  echo "Getting private "
  if echo $state | grep 'active'; then
      instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
      echo "Instance ID: $instanceId"
      nonPrimaryPrivateAddress=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId |jq -r '.Reservations[0].Instances[0].NetworkInterfaces[] | select(.Description | contains("External")) | .PrivateIpAddresses[] | select(.Primary==false)')
      echo "Secondary Address: $nonPrimaryPrivateAddress"
  elif echo $state2 | grep 'active'; then
      instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2InstanceId")|.OutputValue')
      echo "Instance ID: $instanceId"
      nonPrimaryPrivateAddress=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId |jq -r '.Reservations[0].Instances[0].NetworkInterfaces[] | select(.Description | contains("External")) | .PrivateIpAddresses[] | select(.Primary==false)')
      echo "Secondary Address: $nonPrimaryPrivateAddress"
  fi
  if echo $nonPrimaryPrivateAddress | grep 'Association'; then
      echo "SUCCESS"
  fi
else
  state=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh show sys failover')
  state2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP2" 'tmsh show sys failover')
  echo "State: $state"
  echo "State2: $state2"
  echo "Getting private "
  if echo $state | grep 'active'; then
      instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
      echo "Instance ID: $instanceId"
      nonPrimaryPrivateAddress=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId |jq -r '.Reservations[0].Instances[0].NetworkInterfaces[] | select(.Description | contains("External")) | .PrivateIpAddresses[] | select(.Primary==false) | .PrivateIpAddress')
      echo "Secondary Address: $nonPrimaryPrivateAddress"
      vs_address=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh list ltm virtual-address | grep address | cut -d " " -f3')
      echo "VS Address: $vs_address"
  elif echo $state2 | grep 'active'; then
      instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2InstanceId")|.OutputValue')
      echo "Instance ID: $instanceId"
      nonPrimaryPrivateAddress=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId |jq -r '.Reservations[0].Instances[0].NetworkInterfaces[] | select(.Description | contains("External")) | .PrivateIpAddresses[] | select(.Primary==false) | .PrivateIpAddress | @csv')
      echo "Secondary Address: $nonPrimaryPrivateAddress"
      vs_address=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh list ltm virtual-address | grep address | cut -d " " -f3')
      echo "VS Address: $vs_address"
  fi
  if [[ "$vs_address" == *"$nonPrimaryPrivateAddress"* ]]; then
      echo "SUCCESS"
  fi
fi