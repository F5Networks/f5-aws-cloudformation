#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 80

vpc_response=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc 2>&1)

# verify delete
if echo $vpc_response | grep 'does not exist'; then
  echo "SUCCESS"
else
  echo "FAILED"
fi