#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 25

# locate bigip ip addresses: used for all tests
case <SOLUTION TYPE> in
autoscale)
  bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
  instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
  IP=$(aws ec2 describe-instances --instance-ids $instanceId --region <REGION> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
  echo "Bigip1Url=$IP" ;;
ha)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
    echo "instanceId=$instanceId"
    IP=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "Bigip1Url=$IP"
    instanceId2=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2InstanceId")|.OutputValue')
    echo "instanceId=$instanceId2"
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
    instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
    echo "instanceId=$instanceId"
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


# Locate secondary ip addresses on aws instances
case $number_bigips in
1)
  # find bigip1 secondary private ip address
  case <NIC COUNT> in
  1)
    secondary_ip=$(aws ec2 describe-instances --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[].NetworkInterfaces[].PrivateIpAddresses[]|select (.Primary==true)|.PrivateIpAddress')  ;;
  *)
    secondary_ip=$(aws ec2 describe-instances --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[].NetworkInterfaces[].PrivateIpAddresses[]|select (.Primary==false)|.PrivateIpAddress')  ;;
  esac
  echo "SecondaryIp:$secondary_ip"
  ssh-keygen -R $IP 2>/dev/null  ;;
2)
  # find bigip1 secondary private ip address
  secondary_ip=$(aws ec2 describe-instances --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[].NetworkInterfaces[].PrivateIpAddresses[]|select (.Primary==false)|.PrivateIpAddress')
  echo "SecondaryIp:$secondary_ip"
  # find bigip2 secondary private ip address
  secondary_ip2=$(aws ec2 describe-instances --region <REGION> --instance-ids $instanceId2|jq -r '.Reservations[0].Instances[].NetworkInterfaces[].PrivateIpAddresses[]|select (.Primary==false)|.PrivateIpAddress')
  echo "SecondaryIp2:$secondary_ip2"
  ssh-keygen -R $IP 2>/dev/null
  ssh-keygen -R $IP2 2>/dev/null  ;;
esac

# curl app ip for traffic test
if [[ "<PUBLIC IP>" == "Yes" ]]; then
  # find external secondary public ip address
  ext_secondary_ip=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1VipEipAddress")|.OutputValue|split(":")[1]|.[2:]')
  echo "External Secondary Ip:$ext_secondary_ip"
  result=$(curl http://${ext_secondary_ip})
else
  if [[ "<CLUSTER TYPE>" == "same" ]]; then
    secondary_ip=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh list ltm virtual-address | grep address | cut -d " " -f3')
  else
    state=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh show sys failover')
    state2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP2" 'tmsh show sys failover')
    if echo $state | grep 'active'; then
    secondary_ip=$secondary_ip
    else
    secondary_ip=$secondary_ip2
    fi
  fi
  echo "Secondary ip: $secondary_ip"
  result=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} "curl http://${secondary_ip}")
  ssh-keygen -R $bastion 2>/dev/null
fi

# evaluate result
if echo $result | grep 'Demo App'; then
    echo "SUCCESS"
else
    echo "FAILED"
fi
