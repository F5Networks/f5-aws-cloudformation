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
# temp setting until cfe bz resolved (can only have one vs with same-az solution)
if [[ "<CLUSTER TYPE>" == "same" ]]; then
  number_bigips=1
  echo "Number of bigips is equal to:$number_bigips"
elif [[ -n "$IP" && -n "$IP2" ]]; then
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
  echo "SecondaryIp:$secondary_ip" ;;
2)
  # find bigip1 secondary private ip address
  secondary_ip=$(aws ec2 describe-instances --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[].NetworkInterfaces[].PrivateIpAddresses[]|select (.Primary==false)|.PrivateIpAddress')
  echo "SecondaryIp:$secondary_ip"
  # find bigip2 secondary private ip address
  secondary_ip2=$(aws ec2 describe-instances --region <REGION> --instance-ids $instanceId2|jq -r '.Reservations[0].Instances[].NetworkInterfaces[].PrivateIpAddresses[]|select (.Primary==false)|.PrivateIpAddress')
  echo "SecondaryIp2:$secondary_ip2"  ;;
esac

# determine webserver private url
webserver=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="webserverPrivateIp")|.OutputValue')
echo "Webserver: $webserver"
# Run TMSH commands to set pool and virtuals
case $number_bigips in
1)
  ssh-keygen -R $IP1 2>/dev/null
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh create ltm pool dewpt-pool members add { $webserver:80 } monitor http"
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh create ltm virtual /Common/dewpt-80 { destination ${secondary_ip}:80 mask 255.255.255.255 ip-protocol tcp pool /Common/dewpt-pool profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }"
    result=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh list ltm virtual')
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh save /sys config"
  else
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh create ltm pool dewpt-pool members add { $webserver:80 } monitor http"
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh create ltm virtual /Common/dewpt-80 { destination ${secondary_ip}:80 mask 255.255.255.255 ip-protocol tcp pool /Common/dewpt-pool profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }"
    result=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh list ltm virtual')
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh save /sys config"
  fi ;;
2)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh create ltm pool dewpt-pool members add { $webserver:80 } monitor http"
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh create ltm virtual /Common/dewpt-80 { destination ${secondary_ip}:80 mask 255.255.255.255 ip-protocol tcp pool /Common/dewpt-pool profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }"
    result=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh list ltm virtual')
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh create ltm virtual /Common/dewpt2-80 { destination ${secondary_ip2}:80 mask 255.255.255.255 ip-protocol tcp pool /Common/dewpt-pool profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }"
    result2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP2} 'tmsh list ltm virtual')
    if [[ "<CLUSTER TYPE>" == "across" ]]; then
        ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh modify ltm virtual-address ${secondary_ip2} traffic-group none"
        ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh modify ltm virtual-address ${secondary_ip} traffic-group none"
    fi
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} "tmsh save /sys config"
  else
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh create ltm pool dewpt-pool members add { $webserver:80 } monitor http"
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh create ltm virtual /Common/dewpt-80 { destination ${secondary_ip}:80 mask 255.255.255.255 ip-protocol tcp pool /Common/dewpt-pool profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }"
    result=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh list ltm virtual')
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh create ltm virtual /Common/dewpt2-80 { destination ${secondary_ip2}:80 mask 255.255.255.255 ip-protocol tcp pool /Common/dewpt-pool profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }"
    result2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP2" 'tmsh list ltm virtual')
    if [[ "<CLUSTER TYPE>" == "across" ]]; then
        ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh modify ltm virtual-address ${secondary_ip} traffic-group none"
        ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh modify ltm virtual-address ${secondary_ip2} traffic-group none"
    fi
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh save /sys config"
  fi ;;
esac

# evaluate results
if [[ "$number_bigips" = 1 ]]; then
  if echo $result | grep 'dewpt-80'; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi
elif [[ "$number_bigips" = 2 ]]; then
  if echo $result | grep 'dewpt-80' && echo $result2 | grep 'dewpt2-80'; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi
fi
