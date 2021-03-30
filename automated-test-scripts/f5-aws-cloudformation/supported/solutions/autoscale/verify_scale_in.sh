#  expectValue = "PASS"
#  scriptTimeout = 2
#  replayEnabled = true
#  replayTimeout = 30

# AWS autoscale verify scale in

bigipAutoscaleGroup=`aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|grep -A 1 '"OutputKey": "bigipAutoscaleGroup"'| grep OutputValue|cut -f 4 -d '"'`
instances=`aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-names $bigipAutoscaleGroup|grep InstanceId|wc -l`
if [ "$instances" -eq "<MIN INSTANCES>" ]; then 
    echo "PASS"
else
    echo "FAIL"
fi