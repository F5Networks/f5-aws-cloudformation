#  expectValue = "PASS"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

case <AUTOSCALE DNS TYPE> in  
via-dns)
    aws cloudformation delete-stack --region <REGION> --stack-name <STACK NAME>-gtm
    echo "PASS"  ;;
*)
    echo "No GTM present"
    echo "PASS"  ;;
esac