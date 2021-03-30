#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 120

# Verify highbytes alarm triggered from generate_traffic test
response=$(aws cloudwatch describe-alarms --region <REGION> |jq -r '.MetricAlarms[] |select (.StateValue=="ALARM")|.AlarmName')

# force execute autoscaling scale down policy
policy_name1=$(aws autoscaling describe-policies --region <REGION> | jq -r '.ScalingPolicies[]|select (.PolicyName |contains("<STACK NAME>-BigipScaleDownPolicy"))|.PolicyName')
echo "Policy Name:$policy_name1"
group_name1=$(aws autoscaling describe-policies --region <REGION> | jq -r '.ScalingPolicies[]|select (.PolicyName |contains("<STACK NAME>-BigipScaleDownPolicy"))|.AutoScalingGroupName')
echo "Group Name:$group_name1"
response1=$(aws autoscaling execute-policy --auto-scaling-group-name $group_name1 --policy-name $policy_name1 --region <REGION> --no-honor-cooldown)
echo "Response1:$response1"

echo "Response:$response"
  if echo $response | grep '<STACK NAME>-BigipLowbytesAlarm'; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi