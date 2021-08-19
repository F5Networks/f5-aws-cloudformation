#  expectValue = 'AUTO_PASSED'
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 5

rm -f /tmp/<TEMPLATE NAME>
mkdir -p /tmp/<DEWPOINT JOB ID>
echo "template url: <TEMPLATE URL>"
curl -k <TEMPLATE URL> -o /tmp/<DEWPOINT JOB ID>/<TEMPLATE NAME>
echo "uploading local bigiq template"
curl -k file://$PWD/automated-test-scripts/f5-aws-cloudformation/common/f5-existing-stack-byol-2nic-bigiq-licmgmt.template -o /tmp/<DEWPOINT JOB ID>/f5-existing-stack-byol-2nic-bigiq-licmgmt.template
curl -k file://$PWD/automated-test-scripts/f5-aws-cloudformation/common/test-environment.template -o /tmp/<DEWPOINT JOB ID>/test-environment.template
# r=$(date +%s | sha256sum | base64 | head -c 32)
bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
aws s3 mb --region <REGION> s3://"$bucket_name"
aws s3api put-bucket-tagging --bucket $bucket_name  --tagging 'TagSet=[{Key=delete,Value=True},{Key=creator,Value=dewdrop}]'
#aws s3 cp /tmp/<TEMPLATE NAME> s3://"$bucket_name"
OUTPUT=$(aws s3 cp --region <REGION> /tmp/<DEWPOINT JOB ID>/<TEMPLATE NAME> s3://"$bucket_name" --acl public-read 2>&1)
BIGIQ_OUTPUT=$(aws s3 cp --region <REGION> /tmp/<DEWPOINT JOB ID>/f5-existing-stack-byol-2nic-bigiq-licmgmt.template s3://"$bucket_name" --acl public-read 2>&1)
TEST_TEMPLATE_OUTPUT=$(aws s3 cp --region <REGION> /tmp/<DEWPOINT JOB ID>/test-environment.template s3://"$bucket_name" --acl public-read 2>&1)
echo '------'
echo "OUTPUT = $OUTPUT"
echo "BIGIQ_OUTPUT = $BIGIQ_OUTPUT"
echo "TEST_TEMPLATE_OUTPUT = $TEST_TEMPLATE_OUTPUT"
echo '------'
if grep -q failed <<< "$OUTPUT" ; then
    echo AUTO_FAILED
elif grep -q failed <<< "$BIGIQ_OUTPUT" ; then
    echo AUTO_FAILED
elif grep -q failed <<< "$TEST_TEMPLATE_OUTPUT" ; then
    echo AUTO_FAILED
else
	echo AUTO_PASSED
fi
