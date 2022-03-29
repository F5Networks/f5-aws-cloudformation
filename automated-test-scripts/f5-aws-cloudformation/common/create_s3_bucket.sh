#  expectValue = 'AUTO_PASSED'
#  expectFailValue = "Failed"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 5


rm -f /tmp/<TEMPLATE NAME>
TMP_DIR='/tmp/<DEWPOINT JOB ID>'

bigiq_password='NOT_DEPLOYING_BIGIQ'
if [[ "<LICENSE TYPE>" == "bigiq" ]]; then
    if [ -f "${TMP_DIR}/bigiq_info.json" ]; then
        echo "Found existing BIG-IQ"
        cat ${TMP_DIR}/bigiq_info.json
        bigiq_stack_name=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_stack_name)
        bigiq_address=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_address)
        bigiq_password=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_password)
    else
        echo "Failed - No BIG-IQ found"
    fi
fi
echo ${bigiq_password} >> /tmp/bigiq.txt

echo "template url: <TEMPLATE URL>"
curl -k <TEMPLATE URL> -o /tmp/<DEWPOINT JOB ID>/<TEMPLATE NAME>

echo "uploading local bigiq template"
curl -k file://$PWD/automated-test-scripts/f5-aws-cloudformation/common/f5-existing-stack-byol-2nic-bigiq-licmgmt.template -o /tmp/<DEWPOINT JOB ID>/f5-existing-stack-byol-2nic-bigiq-licmgmt.template
curl -k file://$PWD/automated-test-scripts/f5-aws-cloudformation/common/test-environment.template -o /tmp/<DEWPOINT JOB ID>/test-environment.template

bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
aws s3 mb --region <REGION> s3://"$bucket_name"
aws s3api put-bucket-tagging --bucket $bucket_name --tagging 'TagSet=[{Key=delete,Value=True},{Key=creator,Value=dewdrop}]'

OUTPUT=$(aws s3 cp --region <REGION> /tmp/<DEWPOINT JOB ID>/<TEMPLATE NAME> s3://"$bucket_name" --acl public-read 2>&1)
BIGIQ_OUTPUT=$(aws s3 cp --region <REGION> /tmp/<DEWPOINT JOB ID>/f5-existing-stack-byol-2nic-bigiq-licmgmt.template s3://"$bucket_name" --acl public-read 2>&1)
BIGIQ_PASSWORD=$(aws s3 cp --region <REGION> /tmp/bigiq.txt s3://"$bucket_name" --acl public-read 2>&1)
TEST_TEMPLATE_OUTPUT=$(aws s3 cp --region <REGION> /tmp/<DEWPOINT JOB ID>/test-environment.template s3://"$bucket_name" --acl public-read 2>&1)
echo '------'
echo "OUTPUT = $OUTPUT"
echo "BIGIQ_OUTPUT = $BIGIQ_OUTPUT"
echo "BIGIQ_PASSWORD = $BIGIQ_PASSWORD"
echo "TEST_TEMPLATE_OUTPUT = $TEST_TEMPLATE_OUTPUT"
echo '------'
if grep -q failed <<< "$OUTPUT" ; then
    echo AUTO_FAILED
elif grep -q failed <<< "$BIGIQ_OUTPUT" ; then
    echo AUTO_FAILED
elif grep -q failed <<< "$BIGIQ_PASSWORD" ; then
    echo AUTO_FAILED
elif grep -q failed <<< "$TEST_TEMPLATE_OUTPUT" ; then
    echo AUTO_FAILED
else
	echo AUTO_PASSED
fi
