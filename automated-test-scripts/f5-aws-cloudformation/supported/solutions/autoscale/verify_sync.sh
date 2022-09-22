#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 30

# locate bigip ip address: used for all tests
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

# check for sync status green
if [[ "<PUBLIC IP>" == "Yes" ]]; then
    ssh-keygen -R $IP 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem admin@${IP} 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'tmsh show cm sync-status')
else 
    ssh-keygen -R $IP 2>/dev/null
    ssh-keygen -R $bastion 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@${IP} 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@${IP} 'tmsh show cm sync-status')
fi

if echo $response | grep 'All devices in the device group are in sync'; then
    echo "SUCCESS"
fi