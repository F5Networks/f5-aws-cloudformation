#  expectValue = "PASS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15

# AWS autoscale start app server v1.1

if [ <LICENSE TYPE> == 'bigiq' ]
then
  echo PASS
  exit 0
fi

# Find traffic client given region
case <REGION> in
us-west-1)
  awsAppAutoscaleGroupName='DO-NOT-DELETE-dewpt-application-appAutoscaleGroup-MGZSRFJSFG6L'
  ;;
us-west-2)
  awsAppAutoscaleGroupName='DO-NOT-DELETE-dewpt-application-appAutoscaleGroup-10E6H8XZBFYE6'
  ;;
us-east-1)
  awsAppAutoscaleGroupName='DO-NOT-DELETE-dewpt-application-appAutoscaleGroup-1A00SCV3944J5'
  ;;
eu-west-1)
  awsAppAutoscaleGroupName='DO-NOT-DELETE-dewpt-application-appAutoscaleGroup-1QIFFZMVMD9JK'
  ;;
ap-southeast-1)
  awsAppAutoscaleGroupName='DO-NOT-DELETE-dewpt-application-appAutoscaleGroup-1QGZ2VLC21G82'
  ;;
sa-east-1)
  awsAppAutoscaleGroupName='DO-NOT-DELETE-dewpt-application-appAutoscaleGroup-A23S75TWWKOF'
  ;;
*)
  ;;
esac

# Get instance state, expect running
#instanceState=`aws ec2 describe-instances --region <REGION> --instance-ids $trafficClientIid|grep \"Name\":|cut -f 4 -d '"'`

# Save awsAppAutoscaleGroupName to /tmp for later use
echo $awsAppAutoscaleGroupName > /tmp/<TEMPLATE NAME>-awsAppAutoscaleGroupName

# debug statements
echo "awsAppAutoscaleGroupName=$awsAppAutoscaleGroupName"
echo /tmp/<TEMPLATE NAME>-awsAppAutoscaleGroupName
cat /tmp/<TEMPLATE NAME>-awsAppAutoscaleGroupName

# Start one app server in app autoscale group
aws autoscaling set-desired-capacity --region <REGION> --auto-scaling-group-name $awsAppAutoscaleGroupName --desired-capacity 1

echo PASS