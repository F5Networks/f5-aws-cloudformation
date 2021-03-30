#  expectValue = "Stack Events"
#  scriptTimeout = 2
#  replayEnabled = false
#  replayTimeout = 10
set -x
set -v
mkdir -p /tmp/<DEWPOINT JOB ID>
#echo "Github Status"
#curl https://status.github.com/api/status.json?callback-apiStatus
#curl https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/master/dist/f5-cloud-libs.tar.gz -I

echo "Stack Events"
aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>|jq '.StackEvents[]'
IP1=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="device1Url")|.OutputValue|split(":")[1]|.[2:]')

echo "device1Url=$IP1"
ssh-keygen -R $IP1 2>/dev/null

IP2=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2Url")|.OutputValue|split(":")[1]|.[2:]')
echo "Bigip2Url=$IP2"
ssh-keygen -R $IP2 2>/dev/null

LOGS="cfn-init.log ltm install.log network.log onboard.log cluster.log"

if [ -n "$IP1" ]; then
    for LOG in $LOGS; do
        echo "--- Bigip1 $LOG ---"
        if [ "cfn-init.log" = ${LOG} ] || [ "ltm" = ${LOG} ] ; then
            base="/var/log/"
        else
            base="/var/log/cloud/aws/"
        fi
        filename=$(basename ${LOG})
        echo $filename
        echo $base
        scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem admin@${IP1}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
        cat /tmp/<DEWPOINT JOB ID>/${filename}-<REGION> 2>/dev/null
        echo
    done
else
    echo "Bigip1Url not found in stack <STACK NAME>"
fi

if [ -n "$IP2" ]; then
    for LOG in $LOGS; do
        echo "--- Bigip2 $LOG ---"
        filename=$(basename ${LOG})
        echo $filename
        scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem admin@${IP2}:/var/log/${LOG} /tmp/<DEWPOINT JOB ID>/$filename-<REGION>
        cat /tmp/<DEWPOINT JOB ID>/$filename-<REGION> 2>/dev/null
        echo
    done
else
    echo "Bigip2Url not found in stack <STACK NAME>"
fi
rm -rf /tmp/<DEWPOINT JOB ID>