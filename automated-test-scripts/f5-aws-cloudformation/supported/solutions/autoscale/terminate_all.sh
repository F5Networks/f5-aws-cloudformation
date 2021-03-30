#  expectValue = "SUCCESS"
#  scriptTimeout = 1
#  replayEnabled = true
#  replayTimeout = 1
#  expectFailValue = "FAILED"


bigipAutoscaleGroup=`aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|grep -A 1 '"OutputKey": "bigipAutoscaleGroup"'| grep OutputValue|cut -f 4 -d '"'`
instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output json | jq '.[0]' | tr -d '"')
s3Bucket=$(aws s3api list-buckets --query "Buckets[].Name" | jq '.[] | select (contains("<DEWPOINT JOB ID>") and contains("s3bucket"))' | tr -d '"')

echo $instanceId
echo $s3Bucket


availableInstances=$(aws s3 ls "s3://$s3Bucket/instances/" | awk '{print $4}')
echo "Available Instance Ids: $availableInstances"

for id in $availableInstances
do
    echo "Terminating instance id: $id"
    response=$(aws ec2 terminate-instances --region <REGION> --instance-ids $id)

    echo "Instance Termination Response: "
    echo $response

    if echo $response | jq ".TerminatingInstances" | grep -E 'shutting-down|terminated' ; then
        echo "Termination action is validated. Deleting instance: $id metadata from DB"
        echo $(aws s3 rm "s3://$s3Bucket/instances/$id")
    else
        echo 'FAILED'
    fi
done

echo "SUCCESS"
