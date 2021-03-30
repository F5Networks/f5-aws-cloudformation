#  expectValue = "successful"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 20

IP=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
echo "Bigip1Url=$IP"

IP2=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2Url")|.OutputValue|split(":")[1]|.[2:]')
echo "Bigip2Url=$IP2"
SUCCESS="successful"

if [ <CLUSTER TYPE> -eq "across" ]; then
    ssh-keygen -R $IP 2>/dev/null
    ssh-keygen -R $IP2 2>/dev/null
    SELFIP=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh list net self')
    DEVICE_GROUP=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh list cm device-group')
    LOCAL_GW=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'cd / | tmsh list net route recursive')
    echo "${SELFIP}\n${DEVICE_GROUP}\n${LOCAL_GW} 
fi
echo $SUCCESS