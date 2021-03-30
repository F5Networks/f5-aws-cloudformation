#  expectValue = "PASS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15

# AWS autoscale stop app server v1.0
if [ <LICENSE TYPE> == 'bigiq' ]
then
  echo PASS
  exit 0
fi

# Get trafficClientIid from /tmp saved earlier
awsAppAutoscaleGroupName=`cat /tmp/<TEMPLATE NAME>-awsAppAutoscaleGroupName`

# Stop app server in app autoscale group
aws autoscaling set-desired-capacity --region <REGION> --auto-scaling-group-name $awsAppAutoscaleGroupName --desired-capacity 0

# Get instance state, expect stopped
#instanceState=`aws ec2 describe-instances --region <REGION> --instance-ids $trafficClientIid|grep \"Name\":|cut -f 4 -d '"'`

echo PASS