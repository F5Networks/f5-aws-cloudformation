#  expectValue = "SUCCESS"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0
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
case <NIC COUNT> in
2)
  # external security group used for sync
  SecurityGroup=$(aws ec2 describe-security-groups --region <REGION> | jq -r '.SecurityGroups[] | select (.GroupName | contains("<DEWPOINT JOB ID>-bigipExternalSecurityGroup")) | .GroupId')  ;;
3)
  # internal security group used for sync
  SecurityGroup=$(aws ec2 describe-security-groups --region <REGION> | jq -r '.SecurityGroups[] | select (.GroupName | contains("<DEWPOINT JOB ID>-bigipInternalSecurityGroup")) | .GroupId')  ;;
esac

echo "Security Group ID: $SecurityGroup"
echo "Revoking Ingress rule for 1026 port on internal interface. This is done to make Active-Active"

response=$(aws ec2 revoke-security-group-ingress --region <REGION> --group-id $SecurityGroup --protocol udp --port 1026 --source-group $SecurityGroup)

if echo $response | grep 'error'; then
    echo "FAILED"
else
    echo "SUCCESS"
fi



