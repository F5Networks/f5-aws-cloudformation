#  expectValue = "StackId"
#  expectFailValue = "FAILED"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0


TMP_DIR='/tmp/<DEWPOINT JOB ID>'

bigiq_stack_name=$(aws cloudformation describe-stacks --query 'Stacks[?Tags[?Key == `bigiq` && Value == `True`]].{StackName: StackName}' | jq -r .[0].StackName)
bigiq_stack_id=$(aws cloudformation describe-stacks --stack-name $bigiq_stack_name | jq -r .Stacks[0].StackId)
bigiq_stack_status=$(aws cloudformation describe-stacks --stack-name $bigiq_stack_name | jq -r .Stacks[0].StackStatus)
bigiq_stack_region=$(echo $bigiq_stack_id | awk -F '[:]' '{ print $4 }')
bigiq_address=$(aws cloudformation describe-stacks --region $bigiq_stack_region --stack-name $bigiq_stack_name | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="device1ManagementEipAddress")|.OutputValue')
bigiq_password=''

if [ "$bigiq_stack_status" == "CREATE_COMPLETE" ]; then
    bigiq_password=$(echo -n ${bigiq_stack_name} | base64)
    jq -n --arg bigiq_stack_name "$bigiq_stack_name" --arg bigiq_stack_id "$bigiq_stack_id" --arg bigiq_stack_region "$bigiq_stack_region" --arg bigiq_address "$bigiq_address" --arg bigiq_password "$bigiq_password" '{bigiq_stack_name: $bigiq_stack_name, bigiq_stack_id: $bigiq_stack_id, bigiq_stack_region: $bigiq_stack_region, bigiq_address: $bigiq_address, bigiq_password: $bigiq_password}' > ${TMP_DIR}/bigiq_info.json
    cat ${TMP_DIR}/bigiq_info.json
    echo "Found existing BIG-IQ StackId"
else
    if [ "<SCHEDULED BIGIQ>" == "False" ]; then
        echo "FAILED"
    else
        echo "Did not find existing BIG-IQ StackId"
    fi
fi