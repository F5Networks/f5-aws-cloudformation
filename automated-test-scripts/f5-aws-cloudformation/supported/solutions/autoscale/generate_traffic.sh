#  expectValue = "grep java"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15

# AWS autoscale scale out generate traffic v1.0
instance_id=$(aws cloudformation describe-stack-resources --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.StackResources[] | select (.LogicalResourceId=="jmeter")| .PhysicalResourceId')
echo "instance id:$instance_id"

if [[ "<PUBLIC IP>" == "Yes" ]]; then
     jmeter_ip=$(aws ec2 describe-instances --region <REGION> --instance-ids $instance_id | jq -r .Reservations[].Instances[].PublicIpAddress)
     echo "jmeter public ip: $jmeter_ip"
     ssh -o StrictHostKeyChecking=no -i /etc/ssl/private/dewpt_private.pem ubuntu@$jmeter_ip 'bash /home/ubuntu/loadjmeter.sh > /home/ubuntu/loadjmeter.log'
     ssh -o StrictHostKeyChecking=no -i /etc/ssl/private/dewpt_private.pem ubuntu@$jmeter_ip 'cat /home/ubuntu/loadjmeter.log'
else
    jmeter_ip=$(aws ec2 describe-instances --region <REGION> --instance-ids $instance_id | jq -r .Reservations[].Instances[].PrivateIpAddress)
    echo "jmeter private ip: $jmeter_ip"
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion"
    ssh-keygen -R $bastion 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=5 -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" ubuntu@${jmeter_ip} 'bash /home/ubuntu/loadjmeter.sh > /home/ubuntu/loadjmeter.log'
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=5 -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" ubuntu@${jmeter_ip} 'cat /home/ubuntu/loadjmeter.log'
fi
