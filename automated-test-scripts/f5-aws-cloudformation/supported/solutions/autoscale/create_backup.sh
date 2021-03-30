#  expectValue = "SUCCESS"
#  scriptTimeout = 10
#  replayEnabled = true
#  replayTimeout = 5


pathToMetadata='./tmp/dd_id/'
mkdir -p $pathToMetadata


bigipAutoscaleGroup=`aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|grep -A 1 '"OutputKey": "bigipAutoscaleGroup"'| grep OutputValue|cut -f 4 -d '"'`
instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output json | jq '.[0]' | tr -d '"')
s3Bucket=$(aws s3api list-buckets --query "Buckets[].Name" | jq '.[] | select (contains("<DEWPOINT JOB ID>") and contains("s3bucket"))' | tr -d '"')

echo $instanceId
echo $s3Bucket

echo "Getting metadata to identify primary instance-id"
if ! echo $(aws s3api get-object --bucket $s3Bucket --key instances/$instanceId $pathToMetadata/metadata.json | jq '.AcceptRanges') | grep 'bytes'; then
    echo "Problem with getting metadata"
    echo "FAILED"
fi
primaryInstanceId=$(cat "$pathToMetadata/metadata.json" | jq '.primaryStatus.instanceId' | tr -d '"')
echo "Primary Instance Id: $primaryInstanceId"

if [[ "<PUBLIC IP>" == "Yes" ]]; then
  IP=$(aws ec2 describe-instances --instance-ids $primaryInstanceId --region <REGION> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
  echo "Bigip1Url=$IP"
else # Get the private IP address
  IP=$(aws ec2 describe-instances --instance-ids $primaryInstanceId --region <REGION> --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)
  echo "Bigip1Url=$IP"
  bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
  echo "Bastion host:$bastion"
fi


# Executing backup script to create UCS file and upload it to S3 bucket
ssh-keygen -R $IP 2>/dev/null
if [[ "<PUBLIC IP>" == "Yes" ]]; then
  ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'modify auth user admin shell bash'
  response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=8 -i /etc/ssl/private/dewpt.pem admin@${IP} '/config/cloud/aws/run_autoscale_backup.sh')
else
  ssh-keygen -R $bastion 2>/dev/null
  ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@${IP} 'modify auth user admin shell bash'
  response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=8 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=8 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@${IP} '/config/cloud/aws/run_autoscale_backup.sh')
fi
echo "response: $response"

echo "Removing metadata file... $(rm -f "$pathToMetadata/metadata.json")"
echo "SUCCESS"
