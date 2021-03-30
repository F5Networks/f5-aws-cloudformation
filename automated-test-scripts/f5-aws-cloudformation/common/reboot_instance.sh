#  expectValue = "SUCCESS"
#  scriptTimeout = 15
#  replayEnabled = false
#  replayTimeout = 0

# locate bigip ip ids
case <SOLUTION TYPE> in
autoscale)
  bigipAutoscaleGroup=$(aws cloudformation describe-stacks --stack-name <STACK NAME> --region <REGION> --query 'Stacks[0].Outputs[?OutputKey==`bigipAutoscaleGroup`].OutputValue' --output text)
  instanceId=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
  echo "Autoscale, not rebooting" ;;
ha)
  instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
  echo "instanceId=$instanceId"
  echo "Rebooting Bigip1:$instanceId"
  instanceId2=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip2InstanceId")|.OutputValue')
  echo "instanceId2=$instanceId2"
  echo "Rebooting Bigip2:$instanceId2"
  aws ec2 stop-instances --region <REGION> --instance-ids $instanceId
  aws ec2 stop-instances --region <REGION> --instance-ids $instanceId2
  aws ec2 wait instance-stopped --region <REGION> --instance-ids $instanceId
  aws ec2 wait instance-stopped --region <REGION> --instance-ids $instanceId2
  aws ec2 start-instances --region <REGION> --instance-ids $instanceId
  aws ec2 start-instances --region <REGION> --instance-ids $instanceId2 ;;
standalone)
  instanceId=$(aws cloudformation describe-stacks  --region <REGION> --stack-name <STACK NAME>|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1InstanceId")|.OutputValue')
  echo "instanceId=$instanceId"
  echo "Rebooting Bigip1:$instanceId"
  aws ec2 stop-instances --region <REGION> --instance-ids $instanceId
  aws ec2 wait instance-stopped --region <REGION> --instance-ids $instanceId
  aws ec2 start-instances --region <REGION> --instance-ids $instanceId ;;
*)
  echo "No Matching type"
  exit 1 ;;
esac

echo "SUCCESS"