#  expectValue = "StackId"
#  expectFailValue = "Failed"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0


TMP_DIR='/tmp/<DEWPOINT JOB ID>'

# source_ip=""
# while [ "$source_ip" == "" ]
# do
#	sleep 60
#	echo "Waiting 60 seconds..."
#	source_ip=`curl ifconfig.io/ip`
#	echo "source_ip=$source_ip"
# done

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
ext_sub_az2=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="subnet1Az2")|.OutputValue')
echo "external subnet az1:$ext_sub_az2"
int_sub_az2=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-vpc | jq -r '.Stacks[].Outputs[]|select (.OutputKey=="subnet2Az2")|.OutputValue')
echo "internal subnet az1:$int_sub_az2"

# change instance type when using multiple nics
if [[ <NIC COUNT> -ge 4 ]]; then
    # Use the default instance type from the Template
    instance_type='m5.12xlarge'
else
    instance_type=<INSTANCE TYPE>
fi

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

# setup network parms based on number of nics and cluster type
case <NIC COUNT> in
2)
  case <CLUSTER TYPE> in
  same)
    network_param="ParameterKey=managementSubnetAz1,ParameterValue=${mgmt_sub_az1} ParameterKey=subnet1Az1,ParameterValue=${ext_sub_az1} "  ;;
  across)
    network_param="ParameterKey=managementSubnetAz1,ParameterValue=${mgmt_sub_az1} ParameterKey=subnet1Az1,ParameterValue=${ext_sub_az1} \
    ParameterKey=managementSubnetAz2,ParameterValue=${mgmt_sub_az2} ParameterKey=subnet1Az2,ParameterValue=${ext_sub_az2} "  ;;
  esac  ;;
3)
  case <CLUSTER TYPE> in
  same)
    network_param="ParameterKey=managementSubnetAz1,ParameterValue=${mgmt_sub_az1} ParameterKey=subnet1Az1,ParameterValue=${ext_sub_az1} ParameterKey=subnet2Az1,ParameterValue=${int_sub_az1} "  ;;
  across)
    network_param="ParameterKey=managementSubnetAz1,ParameterValue=${mgmt_sub_az1} ParameterKey=subnet1Az1,ParameterValue=${ext_sub_az1} \
    ParameterKey=subnet2Az1,ParameterValue=${int_sub_az1} ParameterKey=managementSubnetAz2,ParameterValue=${mgmt_sub_az2} \
    ParameterKey=subnet1Az2,ParameterValue=${ext_sub_az2} ParameterKey=subnet2Az2,ParameterValue=${int_sub_az2} "  ;;
  esac  ;;
esac

echo "Network_param = $network_param"
echo "Instance Type = $instance_type"

source_cidr='0.0.0.0/0'
echo "source_cidr=$source_cidr"
bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
echo "bucket_name=$bucket_name"

public_ip_param="ParameterKey=provisionPublicIP,ParameterValue=<PUBLIC IP>"
echo "public ip parameter: $public_ip_param"

# determine license parameter
case <LICENSE TYPE> in
bigiq)
  if [ -f "${TMP_DIR}/bigiq_info.json" ]; then
      echo "Found existing BIG-IQ"
      cat ${TMP_DIR}/bigiq_info.json
      bigiq_address=$(cat ${TMP_DIR}/bigiq_info.json | jq -r .bigiq_address)
  else
      echo "Failed - No BIG-IQ found"
  fi
  bigiq_secret_arn="arn:aws:s3:::${bucket_name}/bigiq.txt"
  bigiq_host=${bigiq_address}

  lic_parm="ParameterKey=bigIqAddress,ParameterValue=${bigiq_host} ParameterKey=bigIqLicensePoolName,ParameterValue=<BIGIQ LICENSE POOL> \
  ParameterKey=bigIqPasswordS3Arn,ParameterValue=${bigiq_secret_arn} ParameterKey=bigIqUsername,ParameterValue=admin ParameterKey=bigIqLicenseUnitOfMeasure,ParameterValue=yearly ParameterKey=bigIqLicenseTenant,ParameterValue=<DEWPOINT JOB ID> ParameterKey=bigIqLicenseSkuKeyword1,ParameterValue=BT ParameterKey=bigIqLicenseSkuKeyword2,ParameterValue=1G"  ;;
byol)
  lic_parm="ParameterKey=licenseKey1,ParameterValue=<AUTOFILL EVAL LICENSE KEY> ParameterKey=licenseKey2,ParameterValue=<AUTOFILL EVAL LICENSE KEY 2>" ;;
payg)
  lic_parm=""  ;;
esac
parameters="ParameterKey=allowUsageAnalytics,ParameterValue=<ANALYTICS> \
ParameterKey=Vpc,ParameterValue=$vpc \
ParameterKey=imageName,ParameterValue=<IMAGE NAME> \
ParameterKey=customImageId,ParameterValue=<CUSTOM IMAGE ID> \
ParameterKey=instanceType,ParameterValue=$instance_type \
ParameterKey=restrictedSrcAddress,ParameterValue=$source_cidr \
ParameterKey=restrictedSrcAddressApp,ParameterValue=$source_cidr \
ParameterKey=sshKey,ParameterValue=<SSH KEY> \
ParameterKey=declarationUrl,ParameterValue=<DECLARATION URL> \
ParameterKey=allowPhoneHome,ParameterValue=<PHONEHOME> \
ParameterKey=ntpServer,ParameterValue=<NTP SERVER> \
ParameterKey=bigIpModules,ParameterValue='<BIG IP MODULES>' \
ParameterKey=timezone,ParameterValue=<TIMEZONE> $network_param $lic_parm $public_ip_param"

echo "Parameters:$parameters"

case <REGION> in
cn-north-1 | cn-northwest-1)
  aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME> --tags Key=creator,Value=dewdrop Key=delete,Value=True \
--template-url https://"$bucket_name".s3.<REGION>.amazonaws.com.cn/<TEMPLATE NAME> \
--capabilities CAPABILITY_IAM --parameters $parameters ;;
*)
aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME> --tags Key=creator,Value=dewdrop Key=delete,Value=True \
--template-url https://s3.amazonaws.com/"$bucket_name"/<TEMPLATE NAME> \
--capabilities CAPABILITY_IAM --parameters $parameters ;;
esac

