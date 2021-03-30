#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 50

# locate bigip ip addresses: used for all tests
case <SOLUTION TYPE> in
autoscale)
  signal="SCRIPT_DONE" 
  bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
  instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
  IP=$(aws ec2 describe-instances --instance-ids $instanceId --region <REGION> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
  echo "Bigip1Url=$IP"  ;;
ha)
  signal="PASSWORD_REMOVED"
  case <STACK TYPE> in
  production-stack)
    instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
    echo "instanceId=$instanceId"
    IP=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[0].PrivateIpAddress')
    echo "Bigip1Private=$IP"
    instanceId2=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2InstanceId")|.OutputValue')
    echo "instanceId=$instanceId2"  
    IP2=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId2|jq -r '.Reservations[0].Instances[0].PrivateIpAddress')
    echo "Bigip1Private=$IP2"    
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion" ;;
  existing-stack)
    IP=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "Bigip1Url=$IP"
    IP2=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "Bigip2Url=$IP2"  ;;
  esac ;;
standalone)
  signal="PASSWORD_REMOVED"
  case <STACK TYPE> in
  production-stack)
    instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
    echo "instanceId=$instanceId"
    IP=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[0].PrivateIpAddress')
    echo "Bigip1Private=$IP"
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion" ;;
  existing-stack)
    IP=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "Bigip1Url=$IP" ;;
  esac ;;
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

# test onboard completes by checking for PASSWORD_REMOVED signal
case $number_bigips in
1)
  ssh-keygen -R $IP 2>/dev/null
  ssh-keygen -R $bastion 2>/dev/null
  case <STACK TYPE> in
  existing-stack)
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws')
    echo "response: $response" ;;
  production-stack)
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws')
    echo "response: $response" ;;
  esac ;;  
2)
  ssh-keygen -R $IP 2>/dev/null
  ssh-keygen -R $IP2 2>/dev/null  
  ssh-keygen -R $bastion 2>/dev/null
  case <STACK TYPE> in
  existing-stack)
  ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'modify auth user admin shell bash'
  response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws')
  echo "response: $response"
  ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP2} 'modify auth user admin shell bash'
  response2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP2} 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws')
  echo "response2: $response2" ;;
  production-stack)
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws')
    echo "response: $response"
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP2" 'modify auth user admin shell bash'
    response2=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP2" 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws')
    echo "response: $response2" ;;    
  esac ;;  
esac

if [[ "$number_bigips" = 1 ]]; then
  if echo $response | grep $signal; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi
elif [[ "$number_bigips" = 2 ]]; then
  if echo $response | grep $signal && echo $response2 | grep $signal; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi
fi