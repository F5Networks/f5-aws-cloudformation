#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

# Create Stack
#aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME> --template-url https://s3.amazonaws.com/f5-cft/quickstarts/<VERSION>/templates/f5/master.template --parameters ParameterKey=AllowUsageAnalytics,ParameterValue=<ANALYTICS> ParameterKey=Application1ContainerName,ParameterValue=<APP1> ParameterKey=Application2ContainerName,ParameterValue=<APP2> ParameterKey=BIGIPInstanceType,ParameterValue=<INSTANCE TYPE> ParameterKey=KeyPairName,ParameterValue=<SSH KEY> ParameterKey=AvailabilityZones,ParameterValue=<ZONES> ParameterKey=BIGIPManagementGuiPort,ParameterValue=8443 ParameterKey=BIGIPNotificationEmail,ParameterValue=g.crosby@f5.com ParameterKey=BIGIPScalingMaxSize,ParameterValue=<MAX SIZE> ParameterKey=BIGIPScalingMinSize,ParameterValue=<MIN SIZE> ParameterKey=BIGIPThroughput,ParameterValue=<THROUGHPUT> ParameterKey=DeploymentName,ParameterValue=<STACK NAME> ParameterKey=RemoteAccessCIDR,ParameterValue=<ACCESS>
echo "Hello"