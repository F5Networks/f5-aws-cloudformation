#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0


# Capture environment ids required to create stack
case <AUTOSCALE DNS TYPE> in
via-dns)
  ssh_key="<SSH KEY>"
  vpc=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[] |select (.OutputKey=="Vpc")|.OutputValue')
  echo "VPC:$vpc"
  mgmt_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="managementSubnetAz1")|.OutputValue')
  echo "mgmt subnet az1:$mgmt_sub_az1"
  ext_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="subnet1Az1")|.OutputValue')
  echo "external subnet az1:$ext_sub_az1"
  network_param="ParameterKey=managementSubnetAz1,ParameterValue=${mgmt_sub_az1} ParameterKey=managementSubnetAz1Address,ParameterValue=DYNAMIC ParameterKey=subnet1Az1,ParameterValue=${ext_sub_az1} ParameterKey=subnet1Az1Address,ParameterValue=DYNAMIC"
  source_cidr='0.0.0.0/0'

  # Assemble template parameter
  parameters="ParameterKey=allowUsageAnalytics,ParameterValue=No ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=imageName,ParameterValue=Good25Mbps \
  ParameterKey=instanceType,ParameterValue=m5.xlarge ParameterKey=restrictedSrcAddress,ParameterValue="$source_cidr" ParameterKey=restrictedSrcAddressApp,ParameterValue="$source_cidr" \
  ParameterKey=sshKey,ParameterValue=$ssh_key ParameterKey=ntpServer,ParameterValue=pool.ntp.org ParameterKey=timezone,ParameterValue=US/Pacific \
  $network_param"
  echo "Parameters: $parameters"
  # use published standalone 2nic big-ip byol template
  templateUrl=https://s3.amazonaws.com/f5-cft/f5-existing-stack-payg-2nic-bigip.template

  aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME>-gtm --tags Key=creator,Value=dewdrop Key=delete,Value=True --template-url $templateUrl \
  --capabilities CAPABILITY_IAM --parameters $parameters  ;;

*)
    echo "GTM not required for test:StackId"  ;;
esac
