#  expectValue = 'AUTO_PASSED'
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 5

rm -f /tmp/<TEMPLATE NAME>
mkdir -p /tmp/<DEWPOINT JOB ID>
echo "template url: <TEMPLATE URL>"
curl -k <TEMPLATE URL> -o /tmp/<DEWPOINT JOB ID>/<TEMPLATE NAME>
# r=$(date +%s | sha256sum | base64 | head -c 32)
bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
aws s3 mb --region <REGION> s3://"$bucket_name"
aws s3api put-bucket-tagging --bucket $bucket_name  --tagging 'TagSet=[{Key=delete,Value=True},{Key=creator,Value=dewdrop}]'
#aws s3 cp /tmp/<TEMPLATE NAME> s3://"$bucket_name"
OUTPUT=$(aws s3 cp --region <REGION> /tmp/<DEWPOINT JOB ID>/<TEMPLATE NAME> s3://"$bucket_name" 2>&1)
echo '------'
echo "OUTPUT = $OUTPUT"
echo '------'
if grep -q failed <<< "$OUTPUT" ; then
    echo AUTO_FAILED
else
	echo AUTO_PASSED
fi