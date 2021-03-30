#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 80


case <AUTOSCALE DNS TYPE> in  
via-dns)
  vpc_response=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-gtm 2>&1)  ;;
*)
  echo "GTM not present."
  vpc_response="does not exist"  ;;
esac

# verify delete
if echo $vpc_response | grep 'does not exist'; then
  echo "SUCCESS"
else
  echo "FAILED"
fi