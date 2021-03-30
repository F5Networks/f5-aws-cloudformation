#  expectValue = "PASS"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

# AWS autoscale delete scale-in protect v1.0

bigipAutoscaleGroup=`aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>|jq '.[][].Outputs[] | select(.OutputKey == "bigipAutoscaleGroup") | .OutputValue'`

echo "bigipAutoscaleGroup = ${bigipAutoscaleGroup}"
bigipAutoscaleGroup_sanatized=`echo $bigipAutoscaleGroup | sed s/\"//g`
echo "bigipAutoscaleGroup_sanatized = ${bigipAutoscaleGroup_sanatized}"

for iid in $(aws autoscaling describe-auto-scaling-groups --region <REGION> --auto-scaling-group-name $bigipAutoscaleGroup_sanatized|jq '.[][].Instances[].InstanceId'); do
	echo "iid = ${iid}"
	iid_sanatized=`echo $iid | sed s/\"//g`
	echo "iid_sanatized = ${iid_sanatized}"
    echo "bigipAutoscaleGroup = ${bigipAutoscaleGroup}"
    echo "bigipAutoscaleGroup_sanatized = ${bigipAutoscaleGroup_sanatized}"
	aws autoscaling set-instance-protection --region <REGION> --instance-ids $iid_sanatized --auto-scaling-group-name $bigipAutoscaleGroup_sanatized --no-protected-from-scale-in
done
echo PASS
