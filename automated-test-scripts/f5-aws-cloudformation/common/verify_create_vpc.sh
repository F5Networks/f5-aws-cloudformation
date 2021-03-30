#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 40

# Grab stack info based on stack type
vpc=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc)
events=$(aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>-vpc|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')

# verify stacks created
if echo $vpc | grep 'CREATE_COMPLETE'; then
    echo "SUCCESS"
else
  echo "FAILED"
  echo "Events:$events"
fi