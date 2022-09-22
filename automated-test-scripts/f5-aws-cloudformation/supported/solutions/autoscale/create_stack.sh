#  expectValue = "StackId"
#  expectFailValue = "Failed"
#  scriptTimeout = 10
#  replayEnabled = false
#  replayTimeout = 0


TMP_DIR='/tmp/<DEWPOINT JOB ID>'

if [[ "<PUBLIC IP>" == "Yes" ]]; then
  source_cidr=$(curl ifconfig.me)/32
else
  source_cidr='0.0.0.0/0'
fi
echo "source_cidr=$source_cidr"

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
echo "mgmt subnet az1:$mgmt_sub_az2"
mgmt_parm="$mgmt_sub_az1,$mgmt_sub_az2"
echo "mgmt_parm:$mgmt_parm"
awsBigipElb=$(aws elb describe-load-balancers --load-balancer-name --region <REGION> ELB-dewdrop-<DEWPOINT JOB ID> |jq -r .LoadBalancerDescriptions[].LoadBalancerName)
echo "ELB: $awsBigipElb"
awsAppInternalDnsName=$(aws ec2 describe-instances --region <REGION> |jq -r '.Reservations[].Instances[] |select (.Tags != null) |select (.Tags[].Value=="Webserver:<STACK NAME>-vpc") | .NetworkInterfaces[].Association.PublicDnsName')
echo "ELB DNS: $awsAppInternalDnsName"
image_name=<IMAGE NAME>
echo "image name: $image_name"

# determine bucket where template was copied
bucket_name=`echo <STACK NAME>|cut -c -60|tr '[:upper:]' '[:lower:]'| sed 's:-*$::'`
echo "bucket_name=$bucket_name"

# Build license key parameters and instance type
case <LICENSE TYPE> in
bigiq)
  case <AUTOSCALE TYPE> in
  ltm)
    instance_type="m5.xlarge"  ;;
  waf)
    case <REGION> in
    ca-central-1)
      instance_type="m5.2xlarge"  ;;
    *)
      instance_type="m3.2xlarge"   ;;
    esac  ;;
  esac
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
  case <AUTOSCALE TYPE> in
  ltm)
    instance_type="m5.xlarge"  ;;
  waf)
    case <REGION> in
    ca-central-1)
      instance_type="m5.2xlarge"  ;;
    *)
      instance_type="m3.2xlarge"   ;;
    esac  ;;
  esac
  lic_parm=""  ;;
esac

# Build parameter for DNS autoscale
gtm_member_ip_type="<DNS MEMBER IP TYPE>"
gtm_password_arn="<DNS PASSWORD S3 ARN>"
dns_provider_pool="<DNS PROVIDER POOL>"
case <AUTOSCALE DNS TYPE> in
via-dns)
  if [[ "<PUBLIC IP>" == "Yes" ]]; then
    gtm_ip=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-gtm|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1Url")|.OutputValue|split(":")[1]|.[2:]')
  else
    gtm_ip=$(aws cloudformation describe-stacks --region <REGION> --stack-name <STACK NAME>-gtm|jq -r '.Stacks[0].Outputs[]|select (.OutputKey=="Bigip1ManagementInterfacePrivateIp")|.OutputValue')
  fi
  type_params="ParameterKey=dnsMemberIpType,ParameterValue=$gtm_member_ip_type ParameterKey=dnsMemberPort,ParameterValue=443	\
  ParameterKey=dnsPasswordS3Arn,ParameterValue=$gtm_password_arn	ParameterKey=dnsProviderDataCenter,ParameterValue=test_data_center	\
  ParameterKey=dnsProviderHost,ParameterValue=$gtm_ip ParameterKey=dnsProviderPool,ParameterValue=$dns_provider_pool	\
  ParameterKey=dnsProviderPort,ParameterValue=443 ParameterKey=dnsProviderUser,ParameterValue=admin	"  ;;
via-lb)
  type_params="ParameterKey=bigipElasticLoadBalancer,ParameterValue=$awsBigipElb"  ;;
*)
  type_params=""  ;;
esac

public_ip_param="ParameterKey=provisionPublicIP,ParameterValue=<PUBLIC IP>"
echo "public ip parameter: $public_ip_param"

# Assemble template parameters
templateParams="ParameterKey=allowUsageAnalytics,ParameterValue=<ANALYTICS> ParameterKey=adminUsername,ParameterValue=admin_<CUSTOM USER> \
ParameterKey=applicationPoolTagKey,ParameterValue=Name ParameterKey=applicationPoolTagValue,ParameterValue=Webserver:<STACK NAME>-vpc \
ParameterKey=appInternalDnsName,ParameterValue=$awsAppInternalDnsName ParameterKey=availabilityZones,ParameterValue=\"${az_parm}\" \
ParameterKey=deploymentName,ParameterValue=dewdrop-as-<DEWPOINT JOB ID> \
ParameterKey=customImageId,ParameterValue=OPTIONAL \
ParameterKey=sshKey,ParameterValue=dewpt ParameterKey=subnets,ParameterValue=\"${mgmt_parm}\" ParameterKey=restrictedSrcAddress,ParameterValue=$source_cidr \
ParameterKey=restrictedSrcAddressApp,ParameterValue=0.0.0.0/0 ParameterKey=Vpc,ParameterValue=$vpc ParameterKey=notificationEmail,ParameterValue=<EMAIL> \
ParameterKey=instanceType,ParameterValue=$instance_type ParameterKey=scalingMinSize,ParameterValue=<MIN INSTANCES> ParameterKey=scalingMaxSize,ParameterValue=<MAX INSTANCES> \
ParameterKey=imageName,ParameterValue=$image_name ParameterKey=throughput,ParameterValue=<THROUGHPUT> ParameterKey=declarationUrl,ParameterValue=<DECLARATION URL> ParameterKey=allowPhoneHome,ParameterValue=<PHONEHOME> \
ParameterKey=bigIpModules,ParameterValue='<BIG IP MODULES>' ParameterKey=timezone,ParameterValue=<TIMEZONE> ParameterKey=ntpServer,ParameterValue=<NTP SERVER> ParameterKey=managementGuiPort,ParameterValue=<MGMT PORT> $lic_parm $type_params $public_ip_param"

echo "template parms: $templateParams"

# Run create stack command
aws cloudformation create-stack --disable-rollback --region <REGION> --stack-name <STACK NAME> --tags Key=creator,Value=dewdrop Key=delete,Value=True --template-url https://s3.amazonaws.com/"$bucket_name"/<TEMPLATE NAME> --capabilities CAPABILITY_IAM --parameters $templateParams 2>&1
