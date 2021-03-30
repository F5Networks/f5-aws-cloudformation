#  expectValue = "PASS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 30

# AWS autoscale verify min instances
numberOfMinInstances=<MIN INSTANCES>
echo "numberOfMinInstances=$numberOfMinInstances"

# Get number of healthy instances 
bigipAutoscaleGroup=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|grep -A 1 '"OutputKey": "bigipAutoscaleGroup"'| grep OutputValue|cut -f 4 -d '"')
echo "bigipAutoscaleGroup=$bigipAutoscaleGroup"
numberOfInstancesDetected=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup |grep Healthy |wc -l)
echo "numberOfInstancesDetected=$numberOfInstancesDetected"

if [ $numberOfInstancesDetected -eq $numberOfMinInstances ]; then
	echo "PASS"
else
	echo "FAIL"
fi