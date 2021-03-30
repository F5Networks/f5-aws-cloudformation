#  expectValue = "AWS-SD-App"
#  scriptTimeout = 2
#  replayEnabled = false
#  replayTimeout = 0

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

# test for empty variables and set number of bigips
if [[ -n "$IP" && -n "$IP2" ]]; then
  number_bigips=2
  echo "Number of bigips is equal to:$number_bigips"
elif [ -n "$IP" ]; then
  number_bigips=1
  echo "Number of bigips is equal to:$number_bigips"
else
  echo "Error, number of bigip addressess gathered incorrect:$IP,$IP2"
  exit 1
fi

# Use tags created on Dewpoint Webserver
TAGS_KEY="Dptest"
TAGS_VALUE=<DEWPOINT JOB ID>

# Create the service discovery iApp using tags
App_SD_Name="AWS-SD-App"

# Configure the service discovry via REST
generate_post_data()
{
  cat <<EOF
'{
    "kind":"tm:sys:application:service:servicestate",
    "name":"'$App_SD_Name'",
    "partition":"Common",
    "template": "/Common/f5.service_discovery",
    "templateReference": {
        "link": "https://localhost/mgmt/tm/sys/application/template/~Common~f5.service_discovery?ver=13.0.0"
    },
    "templateModified":"no",
    "trafficGroup": "/Common/traffic-group-1",
    "trafficGroupReference": {
        "link": "https://localhost/mgmt/tm/cm/traffic-group/~Common~traffic-group-1?ver=13.0.0"
    },
    "execute-action":"definition",
    "variables": [
        {
            "name": "cloud__aws_region",
            "encrypted": "no",
            "value": "/#default#"
        },
        {
            "name": "cloud__aws_use_role",
            "encrypted": "no",
            "value": "no"
        },
        {
            "name": "cloud__cloud_provider",
            "encrypted": "no",
            "value": "aws"
        },
        {
            "name": "monitor__frequency",
            "encrypted": "no",
            "value": "30"
        },
        {
            "name": "monitor__http_method",
            "encrypted": "no",
            "value": "GET"
        },
        {
            "name": "monitor__http_version",
            "encrypted": "no",
            "value": "http11"
        },
        {
            "name": "monitor__monitor",
            "encrypted": "no",
            "value": "/#create_new#"
        },
        {
            "name": "monitor__response",
            "encrypted": "no",
            "value": ""
        },
        {
            "name": "monitor__uri",
            "encrypted": "no",
            "value": "/"
        },
        {
            "name": "pool__interval",
            "encrypted": "no",
            "value": "60"
        },
        {
            "name": "pool__member_conn_limit",
            "encrypted": "no",
            "value": "0"
        },
        {
            "name": "pool__member_port",
            "encrypted": "no",
            "value": "80"
        },
        {
            "name": "pool__pool_to_use",
            "encrypted": "no",
            "value": "/#create_new#"
        },
        {
            "name": "pool__public_private",
            "encrypted": "no",
            "value": "private"
        },
        {
            "name": "pool__tag_key",
            "encrypted": "no",
            "value": "'$TAGS_KEY'"
        },
        {
            "name": "pool__tag_value",
            "encrypted": "no",
            "value": "'$TAGS_VALUE'"
        }
    ]
}'
EOF
}
if [[ "<PUBLIC IP>" == "Yes" ]]; then
    curl -sk -u <CUSTOM USER>:'<AUTOFILL PASSWORD>' https://$IP:<MGMT PORT>/mgmt/tm/sys/application/service/ -H 'Content-Type: application/json' -X POST  -d '{
    "kind":"tm:sys:application:service:servicestate",
    "name":"'$App_SD_Name'",
    "partition":"Common",
    "template": "/Common/f5.service_discovery",
    "templateReference": {
        "link": "https://localhost/mgmt/tm/sys/application/template/~Common~f5.service_discovery?ver=13.0.0"
    },
    "templateModified":"no",
    "trafficGroup": "/Common/traffic-group-1",
    "trafficGroupReference": {
        "link": "https://localhost/mgmt/tm/cm/traffic-group/~Common~traffic-group-1?ver=13.0.0"
    },
    "execute-action":"definition",
    "variables": [
        {
            "name": "cloud__aws_region",
            "encrypted": "no",
            "value": "/#default#"
        },
        {
            "name": "cloud__aws_use_role",
            "encrypted": "no",
            "value": "no"
        },
        {
            "name": "cloud__cloud_provider",
            "encrypted": "no",
            "value": "aws"
        },
        {
            "name": "monitor__frequency",
            "encrypted": "no",
            "value": "30"
        },
        {
            "name": "monitor__http_method",
            "encrypted": "no",
            "value": "GET"
        },
        {
            "name": "monitor__http_version",
            "encrypted": "no",
            "value": "http11"
        },
        {
            "name": "monitor__monitor",
            "encrypted": "no",
            "value": "/#create_new#"
        },
        {
            "name": "monitor__response",
            "encrypted": "no",
            "value": ""
        },
        {
            "name": "monitor__uri",
            "encrypted": "no",
            "value": "/"
        },
        {
            "name": "pool__interval",
            "encrypted": "no",
            "value": "60"
        },
        {
            "name": "pool__member_conn_limit",
            "encrypted": "no",
            "value": "0"
        },
        {
            "name": "pool__member_port",
            "encrypted": "no",
            "value": "80"
        },
        {
            "name": "pool__pool_to_use",
            "encrypted": "no",
            "value": "/#create_new#"
        },
        {
            "name": "pool__public_private",
            "encrypted": "no",
            "value": "private"
        },
        {
            "name": "pool__tag_key",
            "encrypted": "no",
            "value": "'$TAGS_KEY'"
        },
        {
            "name": "pool__tag_value",
            "encrypted": "no",
            "value": "'$TAGS_VALUE'"
        }
    ]
}'
else
    ssh -o "StrictHostKeyChecking no" -i /etc/ssl/private/<SSH KEY>.pem ubuntu@${bastion} "curl -sk -u <CUSTOM USER>:'<AUTOFILL PASSWORD>' https://$IP:<MGMT PORT>/mgmt/tm/sys/application/service/ -H 'Content-Type: application/json' -X POST  -d $(generate_post_data)"
fi
