#  expectValue = "PASS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 30

# AWS autoscale verify scale out 

# Get numberOfInstancesExpected
numberOfInstancesExpected=$((<MIN INSTANCES>+1))
echo "numberOfInstancesExpected=$numberOfInstancesExpected"
awsBigipElb="ELB-dewdrop-<DEWPOINT JOB ID>"
# Get number of healthy instances 
bigipAutoscaleGroup=`aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|grep -A 1 '"OutputKey": "bigipAutoscaleGroup"'| grep OutputValue|cut -f 4 -d '"'`
echo "bigipAutoscaleGroup=$bigipAutoscaleGroup"
numberOfInstancesDetected=$(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup |grep Healthy |wc -l)
echo "numberOfInstancesDetected=$numberOfInstancesDetected"

if [ $numberOfInstancesDetected -ge $numberOfInstancesExpected ]; then
	echo "PASS"
else
	echo "FAIL"
fi