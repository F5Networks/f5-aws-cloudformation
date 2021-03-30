#  expectValue = "stopped"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15

# AWS autoscale_stop_traffic_client_v1.1

# Get trafficClientIid from /tmp saved earlier
trafficClientIid=`cat /tmp/<TEMPLATE NAME>-awsAutoscaleTrafficClientIid`

# Stop instance
aws ec2 stop-instances --region <REGION> --instance-ids $trafficClientIid
sleep 60

# Get instance state, expect stopped
instanceState=`aws ec2 describe-instances --region <REGION> --instance-ids $trafficClientIid|grep \"Name\":|cut -f 4 -d '"'`
