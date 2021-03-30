#  expectValue = "PASS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 5

# Use this script to delete bucket created by 'create_s3_bucket.sh'. Do not use when trying to delete bucket created by stack.

bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
aws s3api list-buckets --query "Buckets[].Name" | jq -r .[] | grep -w "$bucket_name"

if [ $? -eq 0 ]; then
    OUTPUT=$(aws s3 rb --region <REGION> s3://"$bucket_name" --force 2>&1)
    echo '------'
    echo "OUTPUT = $OUTPUT"
    echo '------'
    if grep -q remove_bucket: <<< "$OUTPUT" ; then
        echo PASS
    else
        echo FAILED
    fi
else
    echo PASS
fi