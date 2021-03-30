#  expectValue = "running"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15

# AWS autoscale start traffic client v1.1

# Find traffic client given region
case <REGION> in
us-west-1)
  case <LICENSE TYPE> in
  'payg')
      trafficClientIid='i-01590486699a6c30c'
      ;;
  'bigiq')
      trafficClientIid='i-03ac2237050b333c0'
      ;;
  *)
      ;;
  esac
  ;;
us-west-2)
  trafficClientIid='i-06e9ca1f39216852a'
  ;;
us-east-1)
  case <LICENSE TYPE> in
  'payg')
      trafficClientIid='i-088ca6ddecf893dcb'
      ;;
  'bigiq')
      trafficClientIid='i-0fbe00b372711b6b3'
      ;;
  *)
      ;;
  esac
  ;;
us-east-2)
  trafficClientIid='i-061a60c1250efda17'
  ;;
eu-west-1)
  trafficClientIid='i-06277c100b47674ba'
  ;;
ap-southeast-1)
  trafficClientIid='i-02f9b61a6811041a9'
  ;;
sa-east-1)
  trafficClientIid='i-017fc6fe7d96ec9c4'
  ;;
*)
  ;;
esac

# Start instance
aws ec2 start-instances --region <REGION> --instance-ids $trafficClientIid
sleep 30

# Get instance state, expect running
instanceState=`aws ec2 describe-instances --region <REGION> --instance-ids $trafficClientIid|grep \"Name\":|cut -f 4 -d '"'`

# Find public IP of traffic client given Iid
trafficClientPublicIp=`aws ec2 describe-instances --region <REGION> --instance-ids $trafficClientIid|grep PublicIpAddress|cut -f 4 -d '"'`

# Save Iid and public IP of traffic client to /tmp for later use
echo $trafficClientIid > /tmp/<TEMPLATE NAME>-awsAutoscaleTrafficClientIid
echo $trafficClientPublicIp > /tmp/<TEMPLATE NAME>-awsAutoscaleTrafficClientPublicIp

# debug statements
echo "trafficClientIid=$trafficClientIid"
echo "instanceState=$instanceState"
echo "trafficClientPublicIp=$trafficClientPublicIp"
cat /tmp/<TEMPLATE NAME>-awsAutoscaleTrafficClientPublicIp
