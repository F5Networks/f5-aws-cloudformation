#  expectValue = "PASS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 120

## Use this script to delete buckets created by stack. Do not use when creating bucket with create_s3_bucket.sh.
s3Bucket=`aws cloudformation list-stack-resources --region <REGION> --stack-name <STACK NAME>|jq -r '.StackResourceSummaries[]|select (.ResourceType=="AWS::S3::Bucket").PhysicalResourceId'`
echo "s3Bucket=$s3Bucket"
OUTPUT=$(aws s3 rb --region <REGION> s3://"$s3Bucket" --force 2>&1)
echo '------'
echo "OUTPUT = $OUTPUT"
echo '------'
if grep -q remove_bucket: <<< "$OUTPUT" ; then
    echo PASS
else
	echo FAILED
fi