#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 40

# Grab stack info based on stack type
case <AUTOSCALE DNS TYPE> in  
via-dns)
  gtm_stack=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-gtm)
  events=$(aws cloudformation describe-stack-events --region <REGION> --stack-name <STACK NAME>-gtm|jq '.StackEvents[]|select (.ResourceStatus=="CREATE_FAILED")|(.ResourceType, .ResourceStatusReason)') ;;
*)
  gtm_stack="CREATE_COMPLETE"
  echo "GTM not required for test!"  ;;
esac

# verify stacks created
if echo $gtm_stack | grep 'CREATE_COMPLETE'; then
    echo "SUCCESS"
else
  echo "FAILED"
  echo "Events:$events"
fi