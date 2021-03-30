#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15

# Modify high to be really high to allow low to trigger.
# Get highbytesAlarmPhysicalResourceId
highbytesAlarmPhysicalResourceId=`aws cloudformation describe-stack-resources --region <REGION> --stack-name <STACK NAME>|grep BigipHighbytesAlarm|grep PhysicalResourceId|cut -f 4 -d '"'`

# Get highbytesAlarmNamespace
highbytesAlarmNamespace=`aws cloudwatch describe-alarms --region <REGION> --alarm-names $highbytesAlarmPhysicalResourceId|grep Namespace|cut -f 4 -d '"'`

# Get highbytesAlarmActions
highbytesAlarmActions=`aws cloudwatch describe-alarms --region <REGION> --alarm-names $highbytesAlarmPhysicalResourceId|grep BigipScaleUpPolicy|cut -f 2 -d '"'`

# Modify for dewpoint test to scale up at threshold 250000
aws cloudwatch put-metric-alarm --region <REGION> --alarm-name $highbytesAlarmPhysicalResourceId --alarm-actions $highbytesAlarmActions --metric-name throughput-per-sec --namespace $highbytesAlarmNamespace --statistic Average --period 60 --evaluation-periods 1 --threshold 250000.0 --comparison-operator GreaterThanThreshold

# AWS autoscale modify lowbyte alarm

# Get lowbytesAlarmPhysicalResourceId
lowbytesAlarmPhysicalResourceId=`aws cloudformation describe-stack-resources --region <REGION> --stack-name <STACK NAME>|grep BigipLowbytesAlarm|grep PhysicalResourceId|cut -f 4 -d '"'`

# Get lowbytesAlarmNamespace
lowbytesAlarmNamespace=`aws cloudwatch describe-alarms --region <REGION> --alarm-names $lowbytesAlarmPhysicalResourceId|grep Namespace|cut -f 4 -d '"'`

# Get lowbytesAlarmActions
lowbytesAlarmActions=`aws cloudwatch describe-alarms --region <REGION> --alarm-names $lowbytesAlarmPhysicalResourceId|grep BigipScaleDownPolicy|cut -f 2 -d '"'`

# Modify for dewpoint test to scale down in shorter time from 50 mins to 2 mins at threshold 150000
aws cloudwatch put-metric-alarm --region <REGION> --alarm-name $lowbytesAlarmPhysicalResourceId --alarm-actions $lowbytesAlarmActions --metric-name throughput-per-sec --namespace $lowbytesAlarmNamespace --statistic Average --period 60 --evaluation-periods 1 --threshold 150000.0 --comparison-operator LessThanThreshold

# Verify alarm has been set
response=$(aws cloudwatch describe-alarms --region <REGION> |jq -r '.MetricAlarms[].AlarmName')

  if echo $response | grep '<STACK NAME>-BigipLowbytesAlarm'; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi