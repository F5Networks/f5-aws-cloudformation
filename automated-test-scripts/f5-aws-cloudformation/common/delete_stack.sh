#  expectValue = "PASS"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

case <STACK TYPE> in
existing-stack)
  aws cloudformation delete-stack --region <REGION> --stack-name <STACK NAME>
  # If using PublicIP, need to also delete bastion host
  if [[ "<PUBLIC IP>" != "Yes" ]]; then
    aws cloudformation delete-stack --region <REGION> --stack-name <STACK NAME>-bastion
  fi
  echo "PASS" ;;
production-stack)
  aws cloudformation delete-stack --region <REGION> --stack-name <STACK NAME>
  aws cloudformation delete-stack --region <REGION> --stack-name <STACK NAME>-bastion
  echo "PASS" ;;
esac
