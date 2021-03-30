#  expectValue = "SUCCESS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15


# modify autoscaling default cooldown from 25 min to 0 min
group_name=$(aws autoscaling describe-auto-scaling-groups --region <REGION> | jq -r '.AutoScalingGroups[] |select (.AutoScalingGroupARN |contains("<STACK NAME>"))|.AutoScalingGroupName')
aws autoscaling update-auto-scaling-group --region <REGION> --auto-scaling-group-name $group_name --default-cooldown 120
response=$(aws autoscaling describe-auto-scaling-groups --region <REGION> | jq -r '.AutoScalingGroups[] |select (.AutoScalingGroupARN |contains("<STACK NAME>")) | .DefaultCooldown')
echo "Response:$response"

# modify autoscaling cool down to use only 0 seconds for scaleup policy
policy_name1=$(aws autoscaling describe-policies --region <REGION> | jq -r '.ScalingPolicies[]|select (.PolicyName |contains("<STACK NAME>-BigipScaleUpPolicy"))|.PolicyName')
echo "Policy Name:$policy_name1"
group_name1=$(aws autoscaling describe-policies --region <REGION> | jq -r '.ScalingPolicies[]|select (.PolicyName |contains("<STACK NAME>-BigipScaleUpPolicy"))|.AutoScalingGroupName')
echo "Group Name:$group_name1"
response1=$(aws autoscaling put-scaling-policy --auto-scaling-group-name $group_name1 --policy-name $policy_name1 --region <REGION> --cooldown 120 --adjustment-type ChangeInCapacity --scaling-adjustment 1)
echo "Response1:$response1"

# modify autoscaling cool down to use only 0 seconds for scaledown policy
policy_name2=$(aws autoscaling describe-policies --region <REGION> | jq -r '.ScalingPolicies[]|select (.PolicyName |contains("<STACK NAME>-BigipScaleDownPolicy"))|.PolicyName')
echo "Policy Name:$policy_name2"
group_name2=$(aws autoscaling describe-policies --region <REGION> | jq -r '.ScalingPolicies[]|select (.PolicyName |contains("<STACK NAME>-BigipScaleDownPolicy"))|.AutoScalingGroupName')
echo "Group Name:$group_name2"
response2=$(aws autoscaling put-scaling-policy --auto-scaling-group-name $group_name2 --policy-name $policy_name2 --region <REGION> --cooldown 120 --adjustment-type ChangeInCapacity --scaling-adjustment -1)
echo "Response2:$response2"

# Verify policy has changed

  if echo $response1 | grep '<STACK NAME>-BigipScaleUpPolicy'; then
    echo "SUCCESS"
  else
    echo "FAILED"
  fi