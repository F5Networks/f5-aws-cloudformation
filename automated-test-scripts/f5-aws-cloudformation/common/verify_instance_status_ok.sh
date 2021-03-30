#  expectValue = "SUCCESS"
#  scriptTimeout = 5
#  replayEnabled = true
#  replayTimeout = 40

# locate bigip ip ids
case <SOLUTION TYPE> in
autoscale)
  bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
  instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
  echo "Autoscale, not rebooting" ;;
ha)
  instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
  echo "instanceId=$instanceId"
  status=$(aws ec2 describe-instance-status --region <REGION> --instance-ids $instanceId  | jq -r .InstanceStatuses[].SystemStatus.Status)
  instanceId2=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2InstanceId")|.OutputValue')
  echo "instanceId2=$instanceId2"
  status2=$(aws ec2 describe-instance-status --region <REGION> --instance-ids $instanceId2  | jq -r .InstanceStatuses[].SystemStatus.Status) ;;
standalone)
  instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
  echo "instanceId=$instanceId"
  status=$(aws ec2 describe-instance-status --region <REGION> --instance-ids $instanceId  | jq -r .InstanceStatuses[].SystemStatus.Status)
  status2="ok" ;;
*)
  echo "No Matching type"
  exit 1 ;;
esac

if echo $status | grep "ok" && echo $status2 | grep "ok"; then
  echo "SUCCESS: $status $status2"
else
  echo "FAILED: $status $status2"
fi