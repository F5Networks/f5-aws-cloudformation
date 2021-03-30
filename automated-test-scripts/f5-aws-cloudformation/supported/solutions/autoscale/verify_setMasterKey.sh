#  expectValue = "SUCCESS"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 30
#  expectFailValue = "CLOUD_LIBS_ERROR"

cloudLibsError="CLOUD_LIBS_ERROR"

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
fi

ssh-keygen -R $IP 2>/dev/null
if [[ "<PUBLIC IP>" == "Yes" ]]; then
  ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'modify auth user admin shell bash'
  response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'head -n 150 /var/log/cloud/aws/setMasterKey.log ')
else
  ssh-keygen -R $bastion 2>/dev/null
  ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@${IP} 'modify auth user admin shell bash'
  response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@${IP} 'head -n 150 /var/log/cloud/aws/setMasterKey.log ')
fi
echo "SetMaster: $response"


if echo $response | grep $cloudLibsError; then
   echo "$cloudLibsError"
elif echo $response | grep 'wrote master key; calling bigstart restart'; then
   echo "SUCCESS"
else
    echo "FAILED"
fi
