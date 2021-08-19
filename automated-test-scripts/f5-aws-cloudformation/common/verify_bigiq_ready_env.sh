#  expectValue = "license valid"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 60

case <LICENSE TYPE> in
bigiq)
    if [[ "<PUBLIC IP>" == "Yes" ]]; then
        LICENSE_HOST=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>-bigiq|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1Url")|.OutputValue|split(":")[1]|.[2:]')
        echo "BigiqPublicIP=$LICENSE_HOST"
        sshpass -p 'b1gAdminPazz' ssh -o StrictHostKeyChecking=no admin@${LICENSE_HOST} 'bash set-basic-auth on'
        ACTIVATED=$(curl -skvvu admin:'b1gAdminPazz' https://${LICENSE_HOST}/mgmt/cm/device/licensing/pool/utility/licenses | jq .items[0].status)
    else
        LICENSE_HOST=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>-bigiq|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1ManagementInterfacePrivateIp")|.OutputValue')
        echo "BigiqPrivate=$LICENSE_HOST"
        bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP1")|.OutputValue')
        echo "Bastion host:$bastion"
        ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@"$LICENSE_HOST" 'bash set-basic-auth on'
        ACTIVATED=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem -W %h:%p ubuntu@$bastion" admin@"$LICENSE_HOST" 'curl -skvvu admin:'b1gAdminPazz' http://localhost:8100/mgmt/cm/device/licensing/pool/utility/licenses | jq .items[0].status')
    fi

    if [[ $ACTIVATED == \"READY\" ]]; then
        echo "license valid"
    else
        echo "Status: $ACTIVATED"
        echo "sleep 2 minutes before retry"
        sleep 120
    fi
    ;;
*)
    echo "license valid" ;;
esac
