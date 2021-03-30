#  expectValue = "stopped"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 15

# Get jMeter instance id

instance_id=$(aws cloudformation describe-stack-resources --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.StackResources[] | select (.LogicalResourceId=="jmeter")| .PhysicalResourceId')
echo "instance id:$instance_id"

# Stop instance
aws ec2 stop-instances --region <REGION> --instance-ids $instance_id

# Get instance state, expect stopped
instanceState=$(aws ec2 describe-instances --region <REGION> --instance-ids $instance_id|grep \"Name\":|cut -f 4 -d '"')