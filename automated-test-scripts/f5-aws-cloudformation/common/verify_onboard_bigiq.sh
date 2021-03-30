#  expectValue = "NETWORK_DONE"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 20

IP=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1Url")|.OutputValue|split(":")[1]|.[2:]')
echo "device1Url=$IP"
if [ -n "$IP" ]; then
    ssh-keygen -R $IP 2>/dev/null
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem admin@${IP} 'modify auth user admin shell bash'
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'ls -al /tmp/f5-cloud-libs-signals /config/cloud/aws'
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'tmsh modify auth user admin password <AUTOFILL PASSWORD>'
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem admin@${IP} 'set-basic-auth on'
fi