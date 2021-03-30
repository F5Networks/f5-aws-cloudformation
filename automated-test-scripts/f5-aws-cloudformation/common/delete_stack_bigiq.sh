#  expectValue = "PASS"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

case <LICENSE TYPE> in
bigiq)
    aws cloudformation delete-stack --region <REGION> --stack-name <STACK NAME>-bigiq
    echo "PASS"  ;;
*)
    echo "No BIG-IQ present"
    echo "PASS"  ;;
esac