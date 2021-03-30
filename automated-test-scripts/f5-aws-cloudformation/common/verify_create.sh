#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 150

bigip=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>)
events=$(aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')

# Grab stack info based on whether using PublicIP
if [[ "<PUBLIC IP>" == "Yes" ]]; then
    bastion="CREATE_COMPLETE"
else
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion)
    bastion_events=$(aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>-bastion|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')
fi

if echo $bigip | grep 'CREATE_COMPLETE' && echo $bastion | grep 'CREATE_COMPLETE'; then
  echo "SUCCESS"
else
  echo "FAILED"
  echo "EVENTS:${events}/n$bastion_events"
fi
