#  expectValue = "Stack Events"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 10

mkdir -p /tmp/<DEWPOINT JOB ID>

# locate bigip ip addresses: used for all tests
case <SOLUTION TYPE> in
autoscale)
  bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
  instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
  IP=$(aws ec2 describe-instances --instance-ids $instanceId --region <REGION> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
  echo "Bigip1Url=$IP" ;;
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

echo "-------------------------------Stack Events---------------------------------"
aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>|jq '.StackEvents[]'
echo "----------------------------End Stack Events--------------------------------"

LOGS="audit auditd/audit.log restjavad.0.log restnoded.log cloudLibsError.log cfn-init.log install.log network.log createUser.log onboard.log custom-config.log rm-password.log generatePassword.log cluster.log autoscale.log ltm 1nicSetup.log"

if [[ "<STACK TYPE>" == "production-stack" && -n "$IP" ]]; then
  for LOG in $LOGS; do
    echo "------------------------LOG:$LOG ------------------------"
    if [ "cfn-init.log" = ${LOG} ] || [ "ltm" = ${LOG} ] || [ "restjavad.0.log" = "${LOG}" ] || [ "audit" = "${LOG}" ] || [ "auditd/audit.log" = "${LOG}" ]; then
      base="/var/log/"
    elif [ "restnoded.log" = ${LOG} ]; then
      base="/var/log/restnoded/"
    else
      base="/var/log/cloud/aws/"
    fi
    filename=$(basename ${LOG})
    echo $filename
    if [[ "<PUBLIC IP>" == "Yes" ]]; then
      scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem admin@${IP}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
    else
      scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@${IP}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
    fi
    cat /tmp/<DEWPOINT JOB ID>/${filename}-<REGION> 2>/dev/null
    echo
  done
  ssh-keygen -R $IP 2>/dev/null
  ssh-keygen -R $bastion 2>/dev/null
elif [[ "<STACK TYPE>" == "existing-stack" && -n "$IP" ]]; then
  for LOG in $LOGS; do
    echo "------------------------LOG:$LOG ------------------------"
    if [ "cfn-init.log" = ${LOG} ] || [ "ltm" = ${LOG} ] || [ "restjavad.0.log" = "${LOG}" ]; then
      base="/var/log/"
    elif [ "restnoded.log" = ${LOG} ]; then
      base="/var/log/restnoded/"
    else
      base="/var/log/cloud/aws/"
    fi
    filename=$(basename ${LOG})
    echo $filename
    if [[ "<PUBLIC IP>" == "Yes" ]]; then
      scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem admin@${IP}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
    else
      scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@${IP}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
    fi
    cat /tmp/<DEWPOINT JOB ID>/${filename}-<REGION> 2>/dev/null
    echo
  done
  ssh-keygen -R $IP 2>/dev/null
else
  echo "Nothing matched, logs not being collected"
fi
if [[ "<STACK TYPE>" == "production-stack" && -n "$IP2" ]]; then
  for LOG in $LOGS; do
    echo "------------------------LOG:$LOG ------------------------"
    if [ "cfn-init.log" = ${LOG} ] || [ "ltm" = ${LOG} ] || [ "restjavad.0.log" = "${LOG}" ]; then
      base="/var/log/"
    elif [ "restnoded.log" = ${LOG} ]; then
      base="/var/log/restnoded/"
    else
      base="/var/log/cloud/aws/"
    fi
    filename=$(basename ${LOG})
    echo $filename
    if [[ "<PUBLIC IP>" == "Yes" ]]; then
      scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem admin@${IP2}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
    else
      scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@${IP2}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
    fi
    cat /tmp/<DEWPOINT JOB ID>/${filename}-<REGION> 2>/dev/null
    echo
  done
  ssh-keygen -R $IP2 2>/dev/null
  ssh-keygen -R $bastion 2>/dev/null
elif [[ "<STACK TYPE>" == "existing-stack" && -n "$IP2" ]]; then
  for LOG in $LOGS; do
    echo "------------------------LOG:$LOG ------------------------"
    if [ "cfn-init.log" = ${LOG} ] || [ "ltm" = ${LOG} ] || [ "restjavad.0.log" = "${LOG}" ]; then
      base="/var/log/"
    elif [ "restnoded.log" = ${LOG} ]; then
      base="/var/log/restnoded/"
    else
      base="/var/log/cloud/aws/"
    fi
    filename=$(basename ${LOG})
    echo $filename
    if [[ "<PUBLIC IP>" == "Yes" ]]; then
      scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem admin@${IP2}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
    else
      scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p ubuntu@$bastion" admin@${IP2}:${base}${LOG} /tmp/<DEWPOINT JOB ID>/${filename}-<REGION>
    fi
    cat /tmp/<DEWPOINT JOB ID>/${filename}-<REGION> 2>/dev/null
    echo
  done
  ssh-keygen -R $IP2 2>/dev/null
  ssh-keygen -R $bastion 2>/dev/null
else
  echo "Second Big-IP Not Present"
fi
rm -rf /tmp/<DEWPOINT JOB ID>
