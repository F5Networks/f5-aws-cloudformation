#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 180

signal="config_complete"
case <LICENSE TYPE> in
bigiq)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    IP=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>-bigiq|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "BigiqPublicIP=$IP"
    ssh-keygen -R $IP 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'ls -al /config/cloud')
    echo "response: $response"
  else
    IP=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>-bigiq|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1ManagementInterfacePrivateIp")|.OutputValue')
    echo "BigiqPrivate=$IP"
    ssh-keygen -R $IP 2>/dev/null
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion"
    ssh-keygen -R $bastion 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'ls -al /config/cloud')
    echo "response: $response"
  fi ;;
*)
  echo "BIG-IQ not required for test!"
  response="config_complete"  ;;
esac


if echo $response | grep $signal; then
  echo "SUCCESS"
else
  echo "FAILED"
fi
