#  expectValue = "StackId"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0

#source_ip=""
#while [ "$source_ip" == "" ]
#do
#	sleep 60
#	echo "Waiting 60 seconds..."
#	source_ip=`curl ifconfig.io/ip`
#	echo "source_ip=$source_ip"
#done

# Capture environment ids required to create stack
vpc=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[] |select (.OutputKey=="Vpc")|.OutputValue')
echo "VPC:$vpc"
az=($(aws ec2 describe-availability-zones --region <REGION> | jq -r '.AvailabilityZones | map(.ZoneName)| join (" ")'))
echo "AZ's: ${az[@]}"
i="0"
while [ $i -lt 2 ]
do
  export az${i}=${az[$i]}
  i=$[$i+1]
done
az_parm="$az0,$az1"
echo "First 2 Availability Zones used in az_parm: $az_parm"
mgmt_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="managementSubnetAz1")|.OutputValue')
echo "mgmt subnet az1:$mgmt_sub_az1"
mgmt_sub_az2=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="managementSubnetAz2")|.OutputValue')
echo "mgmt subnet az2:$mgmt_sub_az2"
mgmt_parm="$mgmt_sub_az1,$mgmt_sub_az2"
echo "mgmt_parm:$mgmt_parm"
ext_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="subnet1Az1")|.OutputValue')
echo "external subnet az1:$ext_sub_az1"
int_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="subnet2Az1")|.OutputValue')
echo "internal subnet az1:$int_sub_az1"
app_sub_az1=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="Az1ApplicationSubnet")|.OutputValue')
echo "application subnet az1:$app_sub_az1"
instance_type=<INSTANCE TYPE>
# Construct an IP address belong to a specific subnet
#
# usage: get_ip ip offset
#
# NOTE: this is a hack (best guess), It will not work if the constructed IP address is already
# been used
function get_ip() {
    ip=$(echo $1 | cut -d "/" -f 1)
    RET=$(echo $ip | awk -F. '{ printf "%d.%d.%d.%d", $1, $2, $3, $4+'$2' }')
    echo $RET
}

# usage: map string a:b,c:d
function map() {
    RET="$1"
    list=$(echo $2 | tr ';' ' ')
    for i in $list ; do
        kv=($(echo $i | tr ':' ' '))
        RET=$(echo $RET | sed "s/${kv[0]}/${kv[1]}/g")
    done
    echo $RET
}

# setup network parms based on number of nics
case <NIC COUNT> in
1)
  network_param="ParameterKey=managementGuiPort,ParameterValue=8443 ParameterKey=subnet1Az1,ParameterValue=${mgmt_sub_az1} ParameterKey=subnet1Az1Address,ParameterValue=<MGMT_SUBNET_ADDRESS>"  ;;
2)
  network_param="ParameterKey=managementSubnetAz1,ParameterValue=${mgmt_sub_az1} ParameterKey=managementSubnetAz1Address,ParameterValue=<MGMT_SUBNET_ADDRESS> ParameterKey=subnet1Az1,ParameterValue=${ext_sub_az1} ParameterKey=subnet1Az1Address,ParameterValue=<SUBNET1_SUBNET_ADDRESS>" ;;
3)
  network_param="ParameterKey=managementSubnetAz1,ParameterValue=${mgmt_sub_az1} ParameterKey=managementSubnetAz1Address,ParameterValue=<MGMT_SUBNET_ADDRESS> ParameterKey=subnet1Az1,ParameterValue=${ext_sub_az1} ParameterKey=subnet1Az1Address,ParameterValue=<SUBNET1_SUBNET_ADDRESS> ParameterKey=subnet2Az1,ParameterValue=${int_sub_az1} ParameterKey=subnet2Az1Address,ParameterValue=<SUBNET2_SUBNET_ADDRESS>"  ;;
4)
  network_param="ParameterKey=managementSubnetAz1,ParameterValue=${mgmt_sub_az1} ParameterKey=subnet1Az1,ParameterValue=${ext_sub_az1} ParameterKey=subnet2Az1,ParameterValue=${int_sub_az1} ParameterKey=numberOfAdditionalNics,ParameterValue=<MULTI NIC COUNT> ParameterKey=additionalNicLocation,ParameterValue=${app_sub_az1}"  ;;
esac

echo "Network params before mapping: $network_param"
# Get static IP information, if necessary
mgmt_ip="DYNAMIC" ; subnet1_ip="DYNAMIC" ; subnet2_ip="DYNAMIC"
if [[ "<PRIVATE IP TYPE>" == *"STATIC"* ]]; then
    num=$(shuf -i 150-200 -n1)
    num2=$(shuf -i 100-149 -n1)
    # used in all templates
    mgmt_ip=$(get_ip "$(aws ec2 describe-subnets --subnet-ids $mgmt_sub_az1 --region <REGION>| jq .Subnets[0].CidrBlock -r)" ${num})
    if [[ "<NIC COUNT>" = 1 ]]; then
      # used with 1nic only
      mgmt_ip_vip=$(get_ip "$(aws ec2 describe-subnets --subnet-ids $mgmt_sub_az1 --region <REGION>| jq .Subnets[0].CidrBlock -r)" ${num2})
      mgmt_ip="$mgmt_ip,$mgmt_ip_vip"
    fi
    subnet1_ip_external=$(get_ip "$(aws ec2 describe-subnets --subnet-ids $ext_sub_az1 --region <REGION>| jq .Subnets[0].CidrBlock -r)" ${num})
	subnet1_ip_vip=$(get_ip "$(aws ec2 describe-subnets --subnet-ids $ext_sub_az1 --region <REGION>| jq .Subnets[0].CidrBlock -r)" ${num2})
    subnet1_ip="$subnet1_ip_external,$subnet1_ip_vip"
	subnet2_ip=$(get_ip "$(aws ec2 describe-subnets --subnet-ids ${int_sub_az1} --region <REGION>| jq .Subnets[0].CidrBlock -r)" ${num})
fi

map_to_use="<MGMT_SUBNET_ADDRESS>:'${mgmt_ip}';<SUBNET1_SUBNET_ADDRESS>:'${subnet1_ip}';<SUBNET2_SUBNET_ADDRESS>:${subnet2_ip}"
network_param=$(map "$network_param" "$map_to_use")
echo "Network params after mapping: = $network_param"
echo "Management IP = $mgmt_ip"
echo "Subnet1 IP = $subnet1_ip"
echo "Subnet2 IP = $subnet2_ip"
echo "Instance Type = $instance_type"

source_cidr='0.0.0.0/0'
echo "source_cidr=$source_cidr"
bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
echo "bucket_name=$bucket_name"

# determine bigiq license host if required

# determine license parameter
case <LICENSE TYPE> in
bigiq)
  bigiq_host=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-bigiq | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="device1InternalInterfacePrivateIp")|.OutputValue')
  lic_parm="ParameterKey=bigIqAddress,ParameterValue=${bigiq_host} ParameterKey=bigIqLicensePoolName,ParameterValue=<BIGIQ LICENSE POOL> \
  ParameterKey=bigIqPasswordS3Arn,ParameterValue=<BIGIQ LICENSE S3 ARN> ParameterKey=bigIqUsername,ParameterValue=admin ParameterKey=bigIqLicenseUnitOfMeasure,ParameterValue=yearly ParameterKey=bigIqLicenseSkuKeyword1,ParameterValue=BT"  ;;
byol)
  lic_parm="ParameterKey=licenseKey1,ParameterValue=<AUTOFILL EVAL LICENSE KEY>" ;;
payg)
  lic_parm=""  ;;
esac
echo "License parameter: $lic_parm"

public_ip_param="ParameterKey=provisionPublicIP,ParameterValue=<PUBLIC IP>"
echo "public ip parameter: $public_ip_param"

parameters="ParameterKey=allowUsageAnalytics,ParameterValue=<ANALYTICS> ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=imageName,ParameterValue=<IMAGE NAME> ParameterKey=customImageId,ParameterValue=<CUSTOM IMAGE ID> \
ParameterKey=instanceType,ParameterValue=$instance_type ParameterKey=restrictedSrcAddress,ParameterValue=$source_cidr ParameterKey=restrictedSrcAddressApp,ParameterValue=$source_cidr \
ParameterKey=sshKey,ParameterValue=<SSH KEY> ParameterKey=declarationUrl,ParameterValue=<DECLARATION URL> ParameterKey=allowPhoneHome,ParameterValue=<PHONEHOME> ParameterKey=ntpServer,ParameterValue=<NTP SERVER> \
ParameterKey=bigIpModules,ParameterValue='<BIG IP MODULES>' ParameterKey=timezone,ParameterValue=<TIMEZONE> $lic_parm $network_param $public_ip_param"
echo "Parameters:$parameters"

case <REGION> in
cn-north-1 | cn-northwest-1)
  aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME> --tags Key=creator,Value=dewdrop Key=delete,Value=True \
--template-url https://"$bucket_name".s3.<REGION>.amazonaws.com.cn/<TEMPLATE NAME> \
--capabilities CAPABILITY_IAM --parameters $parameters ;;
*)
aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME> --tags Key=creator,Value=dewdrop Key=delete,Value=True \
--template-url https://"$bucket_name".s3.amazonaws.com/<TEMPLATE NAME> \
--capabilities CAPABILITY_IAM --parameters $parameters ;;
esac
