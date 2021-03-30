#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

# Setup varables to use for stack parameters
az=($(aws ec2 describe-availability-zones --region <REGION> | jq -r '.AvailabilityZones | map(.ZoneName)| join (" ")'))
echo "Available AZ's: ${az[@]}"
i="0"
appValue=<DEWPOINT JOB ID>
while [ $i -lt 2 ]
do
  export az${i}=${az[$i]}
  i=$[$i+1]
done
echo "az1:$az0, az2:$az1"

case <REGION> in
eu-north-1)
  instance_type="t3.micro"  ;;
ca-central-1)
  instance_type="t2.micro"  ;;
me-south-1)
  instance_type="t3.micro"  ;;
*)
  instance_type="t2.small"   ;;
esac
echo "Instance:$instance_type"

# If provisioning a Public IP, ensure we create IGW on Subnet
if [[ "<PUBLIC IP>" == "Yes" ]]; then
  useProduction="No"
else
  useProduction="Yes"
fi

case <SOLUTION TYPE> in
autoscale)
  jmeterInstance="Yes"
  elbInstance="Yes" ;;
*)
  jmeterInstance="No"
  elbInstance="No" ;;
esac
parameters="ParameterKey=allowUsageAnalytics,ParameterValue=No ParameterKey=applicationInstanceType,ParameterValue=$instance_type \
ParameterKey=availabilityZone1,ParameterValue=$az0 ParameterKey=availabilityZone2,ParameterValue=$az1 \
ParameterKey=customImageId,ParameterValue=OPTIONAL ParameterKey=declarationUrl,ParameterValue=none \
ParameterKey=sshKey,ParameterValue=dewpt ParameterKey=restrictedSrcAddress,ParameterValue=0.0.0.0/0 \
ParameterKey=restrictedSrcAddressApp,ParameterValue=0.0.0.0/0 ParameterKey=productionStack,ParameterValue=$useProduction \
ParameterKey=jmeterInstance,ParameterValue=$jmeterInstance ParameterKey=elbInstance,ParameterValue=$elbInstance \
ParameterKey=application,ParameterValue=$appValue "
echo "Parameters:$parameters"

case <REGION> in
cn-north-1 | cn-northwest-1)
   aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME>-vpc --tags Key=creator,Value=dewdrop Key=delete,Value=True --template-url https://bastion-hosts.s3.cn-northwest-1.amazonaws.com.cn/test-environment.template --capabilities CAPABILITY_IAM --parameters $parameters ;;
*)
   aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME>-vpc --tags Key=creator,Value=dewdrop Key=delete,Value=True --template-url https://s3.amazonaws.com/f5-cft/QA/test-environment.template --capabilities CAPABILITY_IAM --parameters $parameters ;;
esac
