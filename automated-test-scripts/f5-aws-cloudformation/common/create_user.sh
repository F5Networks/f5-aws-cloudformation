#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 10


# locate bigip ip addresses: used for all tests
case <SOLUTION TYPE> in
autoscale)
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

  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    IP=$(aws ec2 describe-instances --instance-ids $primaryInstanceId --region <REGION> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
    echo "Bigip1Url=$IP"
  else # Get the private IP address
    IP=$(aws ec2 describe-instances --instance-ids $primaryInstanceId --region <REGION> --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)
    echo "Bigip1Url=$IP"
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion"
  fi;;
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

# Create user and test
if [[ "<PUBLIC IP>" == "Yes" ]]; then
  ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'modify auth user admin shell bash'
  response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'tmsh create auth user <CUSTOM USER> partition-access replace-all-with { all-partitions { role admin } } shell bash password "<AUTOFILL PASSWORD>"')
else
  ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'modify auth user admin shell bash'
  response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh create auth user <CUSTOM USER> partition-access replace-all-with { all-partitions { role admin } } shell bash password <AUTOFILL PASSWORD>')
fi
echo "response: $response"

if [[ "<PUBLIC IP>" == "Yes" ]]; then
  check_user=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'tmsh list auth user <CUSTOM USER>')
else
  check_user=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/<SSH KEY>.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh list auth user <CUSTOM USER>')
fi

if echo $check_user | grep role; then
  echo "SUCCESS"
else
  echo "FAILED"
fi
