#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 80


case <LICENSE TYPE> in
bigiq)
  vpc_response=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bigiq 2>&1)  ;;
*)
  echo "BIG-IQ not present."
  vpc_response="does not exist"  ;;
esac

# verify delete
if echo $vpc_response | grep 'does not exist'; then
  echo "SUCCESS"
else
  echo "FAILED"
fi