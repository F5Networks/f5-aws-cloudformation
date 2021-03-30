#  expectValue = "SUCCESS"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

IP=""
bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
if [[ "<PUBLIC IP>" == "Yes" ]]; then
    IP=$(aws ec2 describe-instances --instance-ids $instanceId --region <REGION> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
    echo "Bigip1Url=$IP"
else # Get the private IP address
    IP=$(aws ec2 describe-instances --instance-ids $instanceId --region <REGION> --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)
    echo "Bigip1Url=$IP"
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="EIP")|.OutputValue')
    echo "Bastion host:$bastion"
fi


if [[ "<PUBLIC IP>" == "No" && -n "$IP" ]]; then
    # upload test.ucs file. Contains example bigip.conf, bigip_base.conf, BigDb.dat, and SPEC_Manifest files to use for diff.
    scp -o "StrictHostKeyChecking no" -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" -i /etc/ssl/private/dewpt.pem $PWD/automated-test-scripts/f5-aws-cloudformation/common/test_aws.ucs admin@${IP}:/config/test.ucs
    # create directories and copy test.ucs to /shared/tmp/ucs/ucsOriginal.ucs to mirror autoscale.js behavior when restoring bigip via ucs
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP} 'modify auth user admin shell bash'
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP} 'mkdir -p /shared/tmp/ucs/old; mkdir -p /shared/tmp/ucs/new; mkdir -p /shared/tmp/ucs/ucsRestore; cp /config/test.ucs /shared/tmp/ucs/ucsOriginal.ucs'
    # run update_autoscale_ucs.py using same args as autoscale.js
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP} 'python /config/cloud/aws/node_modules/\@f5devcentral/f5-cloud-libs/scripts/update_autoscale_ucs.py --original-ucs "/shared/tmp/ucs/ucsOriginal.ucs" --updated-ucs "/shared/tmp/ucs/ucsUpdated.ucs" --cloud-provider "aws" --extract-directory "/shared/tmp/ucs/ucsRestore"'
    # unzip original ucs and updated ucs for comparison
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP} 'tar -C /shared/tmp/ucs/new -xvf /shared/tmp/ucs/ucsUpdated.ucs; tar -C /shared/tmp/ucs/old -xvf /shared/tmp/ucs/ucsOriginal.ucs'
    # capture diffs
    bigip_diff=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP} 'diff /var/tmp/ucs/old/config/bigip.conf /var/tmp/ucs/new/config/bigip.conf')
    bigip_base_diff=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP} 'diff /var/tmp/ucs/old/config/bigip_base.conf /var/tmp/ucs/new/config/bigip_base.conf')
    bigip_dat_diff=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP} 'diff /var/tmp/ucs/old/config/BigDB.dat /var/tmp/ucs/new/config/BigDB.dat')
    manifest_diff=$(ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt_private.pem -o ProxyCommand="ssh -o 'StrictHostKeyChecking no' -i /etc/ssl/private/dewpt_private.pem -W %h:%p dewpoint@${BASTION_HOST}" admin@${IP} 'diff /var/tmp/ucs/old/SPEC-Manifest /var/tmp/ucs/new/SPEC-Manifest')
    ssh-keygen -R $IP 2>/dev/null
    ssh-keygen -R $BASTION_HOST 2>/dev/null
elif [[ "<PUBLIC IP>" == "Yes" && -n "$IP" ]]; then
    # upload test.ucs file. Contains example bigip.conf, bigip_base.conf, BigDb.dat, and SPEC_Manifest files to use for diff.
    scp -o "StrictHostKeyChecking no" -i /etc/ssl/private/dewpt.pem $PWD/automated-test-scripts/f5-aws-cloudformation/common/test_aws.ucs admin@${IP}:/config/test.ucs
    # create directories and copy test.ucs to /shared/tmp/ucs/ucsOriginal.ucs to mirror autoscale.js behavior when restoring bigip via ucs
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem admin@${IP} 'mkdir -p /shared/tmp/ucs/old; mkdir -p /shared/tmp/ucs/new; mkdir -p /shared/tmp/ucs/ucsRestore; cp /config/test.ucs /shared/tmp/ucs/ucsOriginal.ucs'
    # run update_autoscale_ucs.py using same args as autoscale.js
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem admin@${IP} 'python /config/cloud/aws/node_modules/\@f5devcentral/f5-cloud-libs/scripts/update_autoscale_ucs.py --original-ucs "/shared/tmp/ucs/ucsOriginal.ucs" --updated-ucs "/shared/tmp/ucs/ucsUpdated.ucs" --cloud-provider "aws" --extract-directory "/shared/tmp/ucs/ucsRestore"'
    # unzip original ucs and updated ucs for comparison
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem admin@${IP} 'tar -C /shared/tmp/ucs/new -xvf /shared/tmp/ucs/ucsUpdated.ucs; tar -C /shared/tmp/ucs/old -xvf /shared/tmp/ucs/ucsOriginal.ucs'
    # capture diffs
    bigip_diff=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem admin@${IP} 'diff /var/tmp/ucs/old/config/bigip.conf /var/tmp/ucs/new/config/bigip.conf')
    bigip_base_diff=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem admin@${IP} 'diff /var/tmp/ucs/old/config/bigip_base.conf /var/tmp/ucs/new/config/bigip_base.conf')
    bigip_dat_diff=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem admin@${IP} 'diff /var/tmp/ucs/old/config/BigDB.dat /var/tmp/ucs/new/config/BigDB.dat')
    manifest_diff=$(ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=6 -i /etc/ssl/private/dewpt.pem admin@${IP} 'diff /var/tmp/ucs/old/SPEC-Manifest /var/tmp/ucs/new/SPEC-Manifest')
    ssh-keygen -R $IP 2>/dev/null
else
  echo "Nothing matched, unable to load test.ucs to bigip"
fi

# evaluate diffs
echo "$bigip_diff"
echo "--------------------"
echo "$bigip_base_diff"
echo "--------------------"
echo "$bigip_dat_diff"
echo "--------------------"
echo "$manifest_diff"

# diff should at a min contain original > ip and new < hostname
if echo $bigip_base_diff | grep -q '10.0.0.229' && echo $bigip_base_diff | grep -q 'ip-10-0-0-229.us-west-2.compute.internal';then
    echo "SUCCESS"
else
    echo "FAILED"
fi
