#  expectValue = "SUCCESS"
#  scriptTimeout = 1
#  replayEnabled = true
#  replayTimeout = 25

dns_provider_pool="<DNS PROVIDER POOL>"
case <AUTOSCALE DNS TYPE> in
via-dns)

    if [[ "<PUBLIC IP>" == "Yes" ]]; then
      gtm=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-gtm|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
      host=https://$gtm
      echo "Host: $host"
      response=$(curl -ku admin:'B!giq2017' --connect-timeout 10 $host/mgmt/tm/gtm/pool/a/$dns_provider_pool/members)
    else
      gtm=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-gtm|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1ManagementInterfacePrivateIp")|.OutputValue')
      host=https://$gtm
      echo "Host: $host"
      bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
      echo "Bastion host:$bastion"
      response=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@"$gtm" 'curl -ku admin:B!giq2017 --connect-timeout 10 '$host'/mgmt/tm/gtm/pool/a/'$dns_provider_pool'/members')
    fi
    echo "Response: $response"  ;;
*)
    echo "Autoscale not using dns!"
    echo "SUCCESS"  ;;
esac

if (( `echo $response | jq '.items | length'` > 0)); then
    echo "SUCCESS"
else
    echo "FAILED"
fi
