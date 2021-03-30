#  expectValue = "SUCCESS"
#  scriptTimeout = 3
#  replayEnabled = true
#  replayTimeout = 150

# Grab stack info based on license type
echo "License type:<LICENSE TYPE>"
case <LICENSE TYPE> in
bigiq)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    bigiq=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bigiq)
    events=$(aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>-bigiq|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')
  else
    bigiq=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bigiq)
    events=$(aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>-bigiq|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')
  fi ;;
*)
  echo "BIG-IQ not required for test!"
  bigiq="CREATE_COMPLETE"
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    echo "Bastion not required for test!"
    bastion="CREATE_COMPLETE"
  else
    bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion)
    bastion_events=$(aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>-bastion|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')
  fi ;;
esac

# Check if bastion host is provisioned
if [[ "<PUBLIC IP>" == "Yes" ]]; then
  echo "Bastion not required for test!"
  bastion="CREATE_COMPLETE"
else
  bastion=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion)
  bastion_events=$(aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>-bastion|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)')
fi

# verify stacks created - verifies both BIGIQ (if created), and Bastion (if created)
if echo $bigiq | grep 'CREATE_COMPLETE' && echo $bastion | grep 'CREATE_COMPLETE'; then
  echo "SUCCESS"
else
  echo "FAILED"
  echo "EVENTS:${events}/n$bastion_events"
fi
