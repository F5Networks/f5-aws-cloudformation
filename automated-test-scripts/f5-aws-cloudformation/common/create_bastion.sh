#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

# Capture environment ids required to create stack
vpc=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[] |select (.OutputKey=="Vpc")|.OutputValue')
echo "VPC:$vpc"
gw_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="subnetGatewayAz1")|.OutputValue')
echo "gw subnet az1:$gw_sub_az1"

# Determine if bastion host is needed for testing
echo "Solution type:<SOLUTION TYPE>"
if [[ "<PUBLIC IP>" == "Yes" ]]; then
  # have public IP - bastion not required
  echo "Bastion Not required: StackId"
else
  # create bastion host stack
  case <REGION> in
  cn-north-1 | cn-northwest-1)
    aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME>-bastion --tags Key=creator,Value=dewdrop Key=delete,Value=True \
    --template-url https://bastion-host.s3.cn-north-1.amazonaws.com.cn/linux-bastion-new.template \
    --capabilities CAPABILITY_IAM --parameters ParameterKey=BastionAMIOS,ParameterValue=Ubuntu-Server-20.04-LTS-HVM \
    ParameterKey=BastionBanner,ParameterValue=https://bastion-host.s3.cn-north-1.amazonaws.com.cn/quickstart-linux-bastion/scripts/banner_message.txt \
    ParameterKey=BastionInstanceType,ParameterValue=m4.xlarge ParameterKey=BastionTenancy,ParameterValue=default \
    ParameterKey=EnableBanner,ParameterValue=false ParameterKey=EnableTCPForwarding,ParameterValue=true \
    ParameterKey=EnableX11Forwarding,ParameterValue=true ParameterKey=KeyPairName,ParameterValue=dewpt ParameterKey=NumBastionHosts,ParameterValue=1 \
    ParameterKey=PublicSubnet1ID,ParameterValue=$gw_sub_az1 ParameterKey=PublicSubnet2ID,ParameterValue=$gw_sub_az1 \
    ParameterKey=QSS3BucketName,ParameterValue=aws-quickstart ParameterKey=QSS3KeyPrefix,ParameterValue=quickstart-linux-bastion/ \
    ParameterKey=RemoteAccessCIDR,ParameterValue=0.0.0.0/0 ParameterKey=VPCID,ParameterValue=$vpc ParameterKey=AlternativeInitializationScript,ParameterValue=https://bastion-host.s3.cn-north-1.amazonaws.com.cn/quickstart-linux-bastion/scripts/bastion_bootstrap.sh ;;
  *)
    aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME>-bastion --tags Key=creator,Value=dewdrop Key=delete,Value=True \
    --template-url https://s3.amazonaws.com/f5-cft/QA/linux-bastion-new.template \
    --capabilities CAPABILITY_IAM --parameters ParameterKey=BastionAMIOS,ParameterValue=Ubuntu-Server-20.04-LTS-HVM \
    ParameterKey=BastionBanner,ParameterValue=https://aws-quickstart.s3.amazonaws.com/quickstart-linux-bastion/scripts/banner_message.txt \
    ParameterKey=BastionInstanceType,ParameterValue=t3.micro ParameterKey=BastionTenancy,ParameterValue=default \
    ParameterKey=EnableBanner,ParameterValue=false ParameterKey=EnableTCPForwarding,ParameterValue=true \
    ParameterKey=EnableX11Forwarding,ParameterValue=true ParameterKey=KeyPairName,ParameterValue=dewpt ParameterKey=NumBastionHosts,ParameterValue=1 \
    ParameterKey=PublicSubnet1ID,ParameterValue=$gw_sub_az1 ParameterKey=PublicSubnet2ID,ParameterValue=$gw_sub_az1 \
    ParameterKey=QSS3BucketName,ParameterValue=aws-quickstart ParameterKey=QSS3KeyPrefix,ParameterValue=quickstart-linux-bastion/ \
    ParameterKey=RemoteAccessCIDR,ParameterValue=0.0.0.0/0 ParameterKey=VPCID,ParameterValue=$vpc ;;
  esac
fi
