#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15

# AWS autoscale modify high bytes alarm

# Get highbytesAlarmPhysicalResourceId
highbytesAlarmPhysicalResourceId=`aws cloudformation describe-stack-resources --region <REGION> --stack-name <STACK NAME>|grep BigipHighbytesAlarm|grep PhysicalResourceId|cut -f 4 -d '"'`

# Get highbytesAlarmNamespace
highbytesAlarmNamespace=`aws cloudwatch describe-alarms --region <REGION> --alarm-names $highbytesAlarmPhysicalResourceId|grep Namespace|cut -f 4 -d '"'`

# Get highbytesAlarmActions
highbytesAlarmActions=`aws cloudwatch describe-alarms --region <REGION> --alarm-names $highbytesAlarmPhysicalResourceId|grep BigipScaleUpPolicy|cut -f 2 -d '"'`

# Modify for dewpoint test to scale up at threshold 15000
aws cloudwatch put-metric-alarm --region <REGION> --alarm-name $highbytesAlarmPhysicalResourceId --alarm-actions $highbytesAlarmActions --metric-name throughput-per-sec --namespace $highbytesAlarmNamespace --statistic Average --period 60 --evaluation-periods 1 --threshold 20000.0 --comparison-operator GreaterThanThreshold


# Verify alarm has been set
response=$(aws cloudwatch describe-alarms --region <REGION> |jq -r '.MetricAlarms[].AlarmName')

  if echo $response | grep '<STACK NAME>-BigipHighbytesAlarm'; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi