#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 120

case <STACK TYPE> in
existing-stack)
  bigip_response=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME> 2>&1)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    bastion_response='does not exist'
  else
    bastion_response=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion 2>&1)
  fi ;;
production-stack)
  bigip_response=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME> 2>&1)
  bastion_response=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bastion 2>&1) ;;
esac

# verify delete
if echo $bigip_response | grep 'does not exist' && echo $bastion_response | grep 'does not exist'; then
  echo "SUCCESS"
else
  echo "FAILED"
fi
