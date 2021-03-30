#  expectValue = "Service Discovery Template"
#  scriptTimeout = 2
#  replayEnabled = false
#  replayTimeout = 0

IP=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME> |jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
# List service discovery iApp
if [ -n "$IP" ]; then
	ssh-keygen -R $IP 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'tmsh list sys application template f5.service_discovery'
fi
echo "Bigip1 Management Address: $IP"