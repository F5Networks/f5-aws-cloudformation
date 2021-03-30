#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 3

bigipAutoscaleGroup=`aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|grep -A 1 '"OutputKey": "bigipAutoscaleGroup"'| grep OutputValue|cut -f 4 -d '"'`
instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output json | jq '.[0]' | tr -d '"')
s3Bucket=$(aws s3api list-buckets --query "Buckets[].Name" | jq '.[] | select (contains("<DEWPOINT JOB ID>") and contains("s3bucket"))' | tr -d '"')

echo $instanceId
echo $s3Bucket

if echo $(aws s3 ls "s3://$s3Bucket/backup/" ) | grep 'ucsAutosave'; then
    echo "UCS file exists under S3 bucket."
    echo "SUCCESS"
fi