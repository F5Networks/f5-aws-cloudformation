#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 50

# locate bigip ip addresses: used for all tests
signal="PASSWORD_REMOVED"
case <AUTOSCALE DNS TYPE> in
via-dns)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    IP=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-gtm|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
    echo "GTM Bigip1Url=$IP"
    ssh-keygen -R $IP 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws')
    echo "response: $response"
  else
    instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>-gtm|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
    echo "instanceId=$instanceId"
    IP=$(aws ec2 describe-instances  --region <REGION> --instance-ids $instanceId|jq -r '.Reservations[0].Instances[0].PrivateIpAddress')
    echo "Bigip1Private=$IP"
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
    echo "Bastion host:$bastion"
    ssh-keygen -R $bastion 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'modify auth user admin shell bash'
    response=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws')
  fi;;
*)
  response=$signal
  echo "GTM not required for test!"  ;;
esac

# evaluate response
if echo $response | grep $signal; then
  echo "Provision GTM"

  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} "tmsh modify auth user admin password 'B!giq2017'"
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem admin@${IP} 'tmsh modify sys provision gtm { level nominal }'
  else
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@"$IP" "tmsh modify auth user admin password 'B!giq2017'"
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@"$IP" 'tmsh modify sys provision gtm { level nominal }'
  fi
  echo "SUCCESS"
else
  echo "FAILED"
fi
