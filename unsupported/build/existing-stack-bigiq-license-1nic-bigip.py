#/usr/bin/python env

from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init, Metadata, InitConfig, InitFiles, InitFile
# from troposphere.ec2 import VPC
# from troposphere.ec2 import InternetGateway
# from troposphere.ec2 import VPCGatewayAttachment
# from troposphere.ec2 import Subnet
# from troposphere.ec2 import RouteTable
# from troposphere.ec2 import Route
# from troposphere.ec2 import SubnetRouteTableAssociation
# from troposphere.ec2 import NetworkInterface
# from troposphere.ec2 import NetworkInterfaceProperty
# from troposphere.ec2 import PrivateIpAddressSpecification
# from troposphere.ec2 import EIPAssociation
# from troposphere.ec2 import EIP
# from troposphere.ec2 import PortRange
# from troposphere.ec2 import Instance
from troposphere.ec2 import *


t = Template()

t.add_version("2010-09-09")

t.add_description("""\
AWS CloudFormation Template for creating an 1nic Big-IP in an existing VPC **WARNING** This template creates Amazon EC2 Instances. You will be billed for the AWS resources used if you create a stack from this template.""")

### BEGIN PARAMETERS

KeyName = t.add_parameter(Parameter(
    "KeyName",
    Type="AWS::EC2::KeyPair::KeyName",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the instance",
))

SSHLocation = t.add_parameter(Parameter(
    "SSHLocation",
    ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
    Description=" The IP address range that can be used to SSH to the EC2 instances",
    Default="0.0.0.0/0",
    MinLength="9",
    AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
    MaxLength="18",
    Type="String",
))

VPC = t.add_parameter(Parameter(
    "VPC",
    ConstraintDescription="Must be an existing VPC within working region.",
    Type="AWS::EC2::VPC::Id",
))

ExternalSubnetId = t.add_parameter(Parameter(
    "ExternalSubnetId",
    ConstraintDescription="Must be subnet ID within existing VPC",
    Type="AWS::EC2::Subnet::Id",
    Description="Public or External subnet ID",
))

BigIPExternalSecurityGroupId = t.add_parameter(Parameter(
    "BigIPExternalSecurityGroupId",
    ConstraintDescription="Must be security group ID within existing VPC",
    Type="AWS::EC2::SecurityGroup::Id",
    Description="Public or External Security Group ID",
))


BigIPInstanceType = t.add_parameter(Parameter(
    "BigIPInstanceType",
    Default="m3.xlarge",
    ConstraintDescription="must be a valid Big-IP EC2 instance type",
    Type="String",
    Description="F5 BIG-IP Virtual Instance Type",
    AllowedValues=["m3.xlarge", "m3.2xlarge", "c1.medium", "c1.xlarge", "cc1.4xlarge", "cc2.8xlarge", "cg1.4xlarge"],
))

BigIPPerformanceType = t.add_parameter(Parameter(
    "BigIPPerformanceType",
    Default="Good",
    ConstraintDescription="Must be a valid F5 Big-IP performance type",
    Type="String",
    Description="F5 BigIP Performance Type",
    AllowedValues=["Good", "Better", "Best"],
))

BigIPManagementGuiPort = t.add_parameter(Parameter(
    "BigIPManagementGuiPort",
    Default="443",
    ConstraintDescription="Must be a valid, unusued port on BIG-IP.",
    Type="Number",
    Description="Port to use for the managment GUI",
))

BigIPAdminUsername = t.add_parameter(Parameter(
    "BigIPAdminUsername",
    Type="String",
    Description="Please enter your BIG-IP Admin Username",
    Default="admin",
    MinLength="1",
    MaxLength="255",
    ConstraintDescription="Please verify your BIG-IP Admin Username",
))

BigIPAdminPassword = t.add_parameter(Parameter(
    "BigIPAdminPassword",
    Type="String",
    Description="Please enter your BIG-IP Admin Password",
    MinLength="1",
    NoEcho=True,
    MaxLength="255",
    ConstraintDescription="Please verify your BIG-IP Admin Password",
))

BigIQAddress = t.add_parameter(Parameter(
    "BigIQAddress",
    MinLength="1",
    ConstraintDescription="Please verify your BIG-IQ Hostname or IP",
    Type="String",
    Description="Please enter your BIG-IQ Hostname or IP",
    MaxLength="255",
))

BigIQUsername = t.add_parameter(Parameter(
    "BigIQUsername",
    MinLength="1",
    ConstraintDescription="Please verify your BIG-IQ Username.",
    Type="String",
    Description="Please enter your BIG-IQ Username",
    MaxLength="255",
))

BigIQPassword = t.add_parameter(Parameter(
    "BigIQPassword",
    Type="String",
    Description="Please enter your BIG-IQ Password",
    MinLength="1",
    NoEcho=True,
    MaxLength="255",
    ConstraintDescription="Please verify your BIG-IQ Password",
))

BigIQLicensePoolUUID = t.add_parameter(Parameter(
    "BigIQLicensePoolUUID",
    MinLength="1",
    ConstraintDescription="Please verify your BIG-IQ License Pool UUID",
    Type="String",
    Description="Please enter your BIG-IQ License Pool UUID",
    MaxLength="255",
))

# WebserverInstanceType = t.add_parameter(Parameter(
#     "WebserverInstanceType",
#     Default="t1.micro",
#     ConstraintDescription="must be a valid EC2 instance type",
#     Type="String",
#     Description="Webserver EC2 instance type",
#     AllowedValues=["t1.micro", "m3.medium", "m3.xlarge", "m2.xlarge", "m3.2xlarge", "c3.large", "c3.xlarge"],
# ))

Webserver = t.add_parameter(Parameter(
    "Webserver",
    ConstraintDescription="Web Server IP used for Big-IP pool Member",
    Type="String",
    Description="Web Server IP used for Big-IP pool member",
))

### BEGIN MAPPINGS

t.add_mapping("BigIPRegionMap",
{u'ap-northeast-1': {u'Best': u'ami-bcf69bbc',
                     u'Better': u'ami-d6f69bd6',
                     u'Good': u'ami-1ef69b1e'},
 u'ap-southeast-1': {u'Best': u'ami-3c9a896e',
                     u'Better': u'ami-249a8976',
                     u'Good': u'ami-029a8950'},
 u'ap-southeast-2': {u'Best': u'ami-bfd69c85',
                     u'Better': u'ami-45d69c7f',
                     u'Good': u'ami-63d69c59'},
 u'eu-west-1': {u'Best': u'ami-3798a740',
                u'Better': u'ami-2b98a75c',
                u'Good': u'ami-f799a680'},
 u'sa-east-1': {u'Best': u'ami-a3952dcf',
                u'Better': u'ami-f69e269a',
                u'Good': u'ami-36962e5a'},
 u'us-east-1': {u'Best': u'ami-98715bf0',
                u'Better': u'ami-f1421d94',
                u'Good': u'ami-03421d66'},
 u'us-west-1': {u'Best': u'ami-a70bc8e3',
                u'Better': u'ami-af0bc8eb',
                u'Good': u'ami-e90bc8ad'},
 u'us-west-2': {u'Best': u'ami-e2d735d1',
                u'Better': u'ami-ccd735ff',
                u'Good': u'ami-36d73505'}}
)

# t.add_mapping("AWSRegionArch2AMI",
# {u'ap-northeast-1': {u'AMI': u'ami-489b8049'},
#  u'ap-southeast-1': {u'AMI': u'ami-0ad2f858'},
#  u'eu-west-1': {u'AMI': u'ami-7dfc720a'},
#  u'sa-east-1': {u'AMI': u'ami-6def5070'},
#  u'us-east-1': {u'AMI': u'ami-00266568'},
#  u'us-west-1': {u'AMI': u'ami-fc8b93b9'},
#  u'us-west-2': {u'AMI': u'ami-71520941'}}
# )


### BEGIN RESOURCES

# VPC = t.add_resource(VPC(
#     "VPC",
#     EnableDnsSupport="true",
#     CidrBlock="10.0.0.0/16",
#     EnableDnsHostnames="true",
#     Tags=Tags(
#         Name=Ref("AWS::StackId"),
#         Application=Ref("AWS::StackId"),
#     ),
# ))

# AZ1ManagementSubnet = t.add_resource(Subnet(
#     "AZ1ManagementSubnet",
#     Tags=Tags(
#         Name="AZ1 Management Subnet",
#         Application=Ref("AWS::StackId"),
#     ),
#     VpcId=Ref("VPC"),
#     CidrBlock="10.0.0.0/24",
#     AvailabilityZone=Ref(AvailabilityZone1),
# ))

# AZ1ExternalSubnet = t.add_resource(Subnet(
#     "AZ1ExternalSubnet",
#     Tags=Tags(
#         Name="AZ1 External Subnet",
#         Application=Ref("AWS::StackId"),
#     ),
#     VpcId=Ref("VPC"),
#     CidrBlock="10.0.1.0/24",
#     AvailabilityZone=GetAtt("AZ1ManagementSubnet", "AvailabilityZone"),
# ))

# AZ1InternalSubnet = t.add_resource(Subnet(
#     "AZ1InternalSubnet",
#     Tags=Tags(
#         Name="AZ1 Internal Subnet",
#         Application=Ref("AWS::StackId"),
#     ),
#     VpcId=Ref("VPC"),
#     CidrBlock="10.0.2.0/24",
#     AvailabilityZone=GetAtt("AZ1ManagementSubnet", "AvailabilityZone"),
# ))

# AZ1ApplicationSubnet = t.add_resource(Subnet(
#     "AZ1ApplicationSubnet",
#     Tags=Tags(
#         Name="AZ1 Application Subnet",
#         Application=Ref("AWS::StackId"),
#     ),
#     VpcId=Ref("VPC"),
#     CidrBlock="10.0.3.0/24",
#     AvailabilityZone=GetAtt("AZ1ManagementSubnet", "AvailabilityZone"),
# ))

# InternetGateway = t.add_resource(InternetGateway(
#     "InternetGateway",
#     Tags=Tags(
#         Application=Ref("AWS::StackId"),
#     ),
# ))

# AttachGateway = t.add_resource(VPCGatewayAttachment(
#     "AttachGateway",
#     VpcId=Ref(VPC),
#     InternetGatewayId=Ref(InternetGateway),
# ))

# ManagementRouteTable = t.add_resource(RouteTable(
#     "ManagementRouteTable",
#     VpcId=Ref("VPC"),
#     Tags=Tags(
#         Name="Management Route Table",
#         Application=Ref("AWS::StackName"),
#         Network="Mgmt",
#     ),
# ))

# ExternalRouteTable = t.add_resource(RouteTable(
#     "ExternalRouteTable",
#     VpcId=Ref("VPC"),
#     Tags=Tags(
#         Name="External Route Table",
#         Application=Ref("AWS::StackName"),
#         Network="External",
#     ),
# ))

# InternalRouteTable = t.add_resource(RouteTable(
#     "InternalRouteTable",
#     VpcId=Ref("VPC"),
#     Tags=Tags(
#         Name="Internal Route Table",
#         Application=Ref("AWS::StackName"),
#         Network="Internal",
#     ),
# ))

# ApplicationRouteTable = t.add_resource(RouteTable(
#     "ApplicationRouteTable",
#     VpcId=Ref("VPC"),
#     Tags=Tags(
#         Name="Application Route Table",
#         Application=Ref("AWS::StackName"),
#         Network="Application",
#     ),
# ))

# ManagementRoute = t.add_resource(Route(
#     "ManagementRoute",
#     GatewayId=Ref("InternetGateway"),
#     DestinationCidrBlock="0.0.0.0/0",
#     RouteTableId=Ref("ManagementRouteTable"),
# ))

# ExternalRoute = t.add_resource(Route(
#     "ExternalRoute",
#     GatewayId=Ref("InternetGateway"),
#     DestinationCidrBlock="0.0.0.0/0",
#     RouteTableId=Ref(ExternalRouteTable),
# ))

# InternalRoute = t.add_resource(Route(
#     "InternalRoute",
#     GatewayId=Ref("InternetGateway"),
#     DestinationCidrBlock="0.0.0.0/0",
#     RouteTableId=Ref(InternalRouteTable),
# ))

# ApplicationRoute = t.add_resource(Route(
#     "ApplicationRoute",
#     GatewayId=Ref(InternetGateway),
#     DestinationCidrBlock="0.0.0.0/0",
#     RouteTableId=Ref(ApplicationRouteTable),
# ))


# ManagementSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
#     "ManagementSubnetRouteTableAssociation",
#     SubnetId=Ref("AZ1ManagementSubnet"),
#     RouteTableId=Ref(ManagementRouteTable),
# ))

# ExternalSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
#     "ExternalSubnetRouteTableAssociation",
#     SubnetId=Ref(AZ1ExternalSubnet),
#     RouteTableId=Ref(ExternalRouteTable),
# ))

# InternalSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
#     "InternalSubnetRouteTableAssociation",
#     SubnetId=Ref(AZ1InternalSubnet),
#     RouteTableId=Ref(InternalRouteTable),
# ))

# ApplicationSubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
#     "ApplicationSubnetRouteTableAssociation",
#     SubnetId=Ref(AZ1ApplicationSubnet),
#     RouteTableId=Ref(ApplicationRouteTable),
# ))


# BigIPExternalSecurityGroup = t.add_resource(SecurityGroup(
#     "BigIPExternalSecurityGroup",
#     SecurityGroupIngress=[{ "ToPort": "22", "IpProtocol": "tcp", "CidrIp": Ref(SSHLocation), "FromPort": "22" }, { "ToPort": Ref(BigIPManagementGuiPort), "IpProtocol": "tcp", "CidrIp": Ref(SSHLocation), "FromPort": Ref(BigIPManagementGuiPort) }, { "ToPort": "80", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "80" }, { "ToPort": "443", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "443" }, { "ToPort": "4353", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "4353" }, { "ToPort": "1026", "IpProtocol": "udp", "CidrIp": "10.0.0.0/16", "FromPort": "1026" }, { "ToPort": "-1", "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0", "FromPort": "-1" }],
#     VpcId=Ref(VPC),
#     GroupDescription="Public or External interface rules",
#     Tags=Tags(
#         Name="BigIP External Security Group",
#         Application=Ref("AWS::StackName"),
#     ),
# ))


# WebserverSecurityGroup = t.add_resource(SecurityGroup(
#     "WebserverSecurityGroup",
#     SecurityGroupIngress=[{ "ToPort": "22", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "22" }, { "ToPort": "80", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "80" }, { "ToPort": "443", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "443" }, { "ToPort": "-1", "IpProtocol": "icmp", "CidrIp": "0.0.0.0/0", "FromPort": "-1" }],
#     VpcId=Ref(VPC),
#     GroupDescription="Enable Access to Webserver",
#     Tags=Tags(
#         Name="Webserver Security Group",
#         Application=Ref("AWS::StackName"),
#     ),
# ))


# NOTE: Need to toggle Subnet Referenced

ExternalInterface = t.add_resource(NetworkInterface(
    "ExternalInterface",
    # SubnetId=Ref(AZ1ExternalSubnet),
    SubnetId=Ref(ExternalSubnetId),
    GroupSet=[Ref(BigIPExternalSecurityGroupId)],
    Description="Public External Interface for the BigIP",
    SecondaryPrivateIpAddressCount="1",
))

ExternalSelfEipAddress = t.add_resource(EIP(
    "ExternalSelfEipAddress",
    Domain="vpc",
))

ExternalSelfEipAssociation = t.add_resource(EIPAssociation(
    "ExternalSelfEipAssociation",
    NetworkInterfaceId=Ref(ExternalInterface),
    AllocationId=GetAtt(ExternalSelfEipAddress, "AllocationId"),
    PrivateIpAddress=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
))



# Note: If existing Webserver input changes
single_nic_metadata = Metadata(
    Init({
        'config': InitConfig(
            files=InitFiles(
                {
                    '/tmp/firstrun.config': InitFile(
                        content=Join('',[
                            "#!/bin/bash\n", 
                            "HOSTNAME=`curl http://169.254.169.254/latest/meta-data/hostname`\n", 
                            #"REGKEY='", Ref(LicenseKey), "'\n", 
                            "TZ='America/Los_Angeles'\n",
                            "BIGIP_DEVICE_ADDRESS='", Ref(ExternalSelfEipAddress),"'\n", 
                            "BIGIP_ADMIN_USERNAME='", Ref(BigIPAdminUsername), "'\n", 
                            "BIGIP_ADMIN_PASSWORD='", Ref(BigIPAdminPassword), "'\n",
                            "BIGIQ_ADDRESS='", Ref(BigIQAddress), "'\n",
                            "BIGIQ_USERNAME='", Ref(BigIQUsername), "'\n",
                            "BIGIQ_PASSWORD='", Ref(BigIQPassword), "'\n",
                            "BIGIQ_LICENSE_POOL_UUID='", Ref(BigIQLicensePoolUUID), "'\n",
                            "MANAGEMENT_GUI_PORT='", Ref(BigIPManagementGuiPort), "'\n", 
                            "APPNAME='demo-app-1'\n", 
                            "VIRTUALSERVERPORT=80\n", 
                            "POOLMEM='", Ref(Webserver), "'\n", 
                            #"POOLMEM='", GetAtt('Webserver','PublicIp'), "'\n", 
                            "POOLMEMPORT=80\n", 
                            "CRT='default.crt'\n", 
                            "KEY='default.key'\n"
                            ]
                        ),
                        mode='000777',
                        owner='root',
                        group='root'
                    ),
                    '/tmp/firstrun.sh': InitFile(
                        content=Join('',[
                            "#!/bin/bash\n",
                            ". /tmp/firstrun.config\n",
                            "FILE=/tmp/firstrun.log\n",
                            "if [ ! -e $FILE ]\n"," then\n",
                            "     touch $FILE\n",
                            "     nohup $0 0<&- &>/dev/null &\n",
                            "     exit\n",
                            "fi\n",
                            "function checkF5Ready {\n",
                            "     sleep 5\n",
                            "     while [[ ! -e '/var/prompt/ps1' ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "done \n",
                            "sleep 5\n",
                            "STATUS=`cat /var/prompt/ps1`\n",
                            "while [[ ${STATUS}x != 'NO LICENSE'x ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "     STATUS=`cat /var/prompt/ps1`\n",
                            "done\n",
                            "echo -n ' '\n",
                            "while [[ ! -e '/var/prompt/cmiSyncStatus' ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "done \n",
                            "STATUS=`cat /var/prompt/cmiSyncStatus`\n",
                            "while [[ ${STATUS}x != 'Standalone'x ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "     STATUS=`cat /var/prompt/cmiSyncStatus`\n",
                            "done\n",
                            "}\n",
                            "function checkStatusnoret {\n",
                            "sleep 10\n",
                            "STATUS=`cat /var/prompt/ps1`\n",
                            "while [[ ${STATUS}x != 'Active'x ]]\n"," do\n",
                            "     echo -n '.'\n",
                            "     sleep 5\n",
                            "     STATUS=`cat /var/prompt/ps1`\n",
                            "done\n",
                            "}\n",
                            "exec 1<&-\n",
                            "exec 2<&-\n",
                            "exec 1<>$FILE\n",
                            "exec 2>&1\n",
                            "checkF5Ready\n",
                            "tmsh modify /sys global-settings hostname ${HOSTNAME}\n",
                            "tmsh mv cm device bigip1 ${HOSTNAME}\n",
                            "tmsh modify auth password root <<< $'${BIGIP_ADMIN_PASSWORD}\n${BIGIP_ADMIN_PASSWORD}\n'\n",
                            "tmsh modify auth user admin password \"'${BIGIP_ADMIN_PASSWORD}'\"\n",
                            "tmsh save /sys config\n",
                            "### BEGIN BIGIQ LICENSE ###\n",
                            "declare -i i\n",
                            "i=0\n",
                            "while ([ -z \"${MACHINE_STATE}\" ] || [ \"${MACHINE_STATE}\" == \"null\" ]);\n",
                            "do\n",
                            "     logger -p local0.info \"license_from_bigiq_debug: Attempting to register the BIGIP: ${BIGIP_DEVICE_ADDRESS} with BIGIQ: ${BIGIQ_ADDRESS}\"\n",
                            "     curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} -o /tmp/add-managed-device-output.json --max-time 15  -H \"Content-Type: application/json\" -X POST -d '{\"deviceAddress\": \"'${BIGIP_DEVICE_ADDRESS}'\", \"username\":\"'${BIGIP_ADMIN_USERNAME}'\", \"password\":\"'${BIGIP_ADMIN_PASSWORD}'\", \"automaticallyUpdateFramework\":\"true\", \"rootUsername\":\"root\", \"rootPassword\":\"'${BIGIP_ROOT_PASSWORD}'\"}' https://${BIGIQ_ADDRESS}/mgmt/cm/cloud/managed-devices\n",
                            "     MACHINE_ID=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .machineId`\n",
                            "     MACHINE_SELFLINK=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .selfLink`\n",
                            "     MACHINE_STATE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .state`\n",
                            "     MACHINE_CODE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .code`\n",
                            "     MACHINE_MESSAGE=`cat /tmp/add-managed-device-output.json | /usr/bin/jq -r .message`\n",
                            "     if [ $i == 10 ]; then\n",
                            "         logger -p local0.err \"license_from_bigiq_debug: EXITING - Could not register the device. CODE: ${MACHINE_CODE}, MESSAGE: ${MACHINE_MESSAGE}\"\n",
                            "         exit 1\n",
                            "    fi\n",
                            "    i=$i+1\n",
                            "    sleep 10\n",
                            "done\n",
                            "i=0\n",
                            "while [ \"${MACHINE_STATE}\" != \"ACTIVE\" ];\n",
                            "do \n",
                            "     MACHINE_STATE=$( curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} --max-time 15 -H \"Content-Type: application/json\" -X GET https://${BIGIQ_ADDRESS}/mgmt/cm/cloud/managed-devices/${MACHINE_ID} | /usr/bin/jq -r .state )\n",
                            "     if [ $i == 30 ] && [ \"${MACHINE_STATE}\" != \"ACTIVE\" ]; then\n",
                            "       logger -p local0.err \"license_from_bigiq_debug: ABORT! Taking too long to register this BIGIP with BIGIQ.\"\n",
                            "       exit 1\n",
                            "     fi\n",
                            "     i=$i+1\n",
                            "     logger -p local0.info \"license_from_bigiq_debug: Machine State: ${MACHINE_STATE}...\"\n",
                            "     sleep 30\n",
                            "done\n",
                            "# Install License From Pool\n",
                            "i=0\n",
                            "while ( [ -z \"$LICENSE_STATE\" ] || [ \"${LICENSE_STATE}\" == \"null\" ] );\n",
                            "do\n",
                            "     logger -p local0.info \"license_from_bigiq_debug: Attempting to get license BIG-IP: ${MACHINE_ID} from license pool: ${BIGIQ_LICENSE_POOL_UUID}\"\n",
                            "     curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} -o /tmp/install-license-output.json --max-time 15  -H \"Content-Type: application/json\" -X POST -d '{\"deviceReference\":{\"link\": \"'${MACHINE_SELFLINK}'\"}}' https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/${BIGIQ_LICENSE_POOL_UUID}/members\n",
                            "     LICENSE_UUID=`cat /tmp/install-license-output.json | /usr/bin/jq -r .uuid`\n",
                            "     LICENSE_STATE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .state`\n",
                            "     LICENSE_CODE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .code`\n",
                            "     LICENSE_MESSAGE=`cat /tmp/install-license-output.json | /usr/bin/jq -r .message`\n",
                            "     if [ $i == 5 ]; then\n",
                            "       logger -p local0.err \"license_from_bigiq_debug: EXITING, could not license the device. CODE: ${LICENSE_CODE}, MESSAGE: ${LICENSE_MESSAGE}\"\n",
                            "       exit 1\n",
                            "     fi\n",
                            "     i=$i+1\n",
                            "     sleep 10\n",
                            "done\n",
                            "i=0\n",
                            "while [ \"${LICENSE_STATE}\" != \"LICENSED\" ];\n",
                            "do\n",
                            "     LICENSE_STATE=$( curl -sSk -u ${BIGIQ_USERNAME}:${BIGIQ_PASSWORD} --max-time 15 -H \"Content-Type: application/json\" -X GET https://${BIGIQ_ADDRESS}/mgmt/cm/shared/licensing/pools/${BIGIQ_LICENSE_POOL_UUID}/members/${LICENSE_UUID} | /usr/bin/jq -r .state )\n",
                            "     if [ \"${LICENSE_STATE}\" == \"INSTALL\" ] ; then\n",
                            "       sleep 5\n",
                            "       continue\n",
                            "     fi\n",
                            "     if [ $i == 5 ] && [ \"${LICENSE_STATE}\" != \"LICENSED\" ]; then\n",
                            "       logger -p local0.info \"license_from_bigiq_debug: BIGIP node not moving to 'LICENSED' state\"\n",
                            "       exit 1\n",
                            "     fi\n",
                            "     i=$i+1\n",
                            "     logger -p local0.info \"license_from_bigiq_debug: License Status: ${LICENSE_STATE}...\"\n",
                            "     sleep 10\n",
                            "done\n",
                            "### END BIGIQ LICENSE ###\n",
                            "checkStatusnoret\n",
                            "sleep 30\n",
                            "tmsh save /sys config\n",
                            "tmsh modify sys db dhclient.mgmt { value disable }\n",
                            "tmsh modify sys ntp timezone ${TZ}\n",
                            "tmsh modify sys ntp servers add { 0.pool.ntp.org 1.pool.ntp.org }\n",
                            "tmsh modify sys global-settings gui-setup disabled\n",
                            "checkStatusnoret\n",
                            "### BZID 572255 = Device Service Clustering Would need to be done here before changing GUI port\n",
                            "tmsh modify sys httpd ssl-port ${MANAGEMENT_GUI_PORT}\n",
                            "tmsh modify net self-allow defaults add { tcp:${MANAGEMENT_GUI_PORT} }\n",
                            "tmsh save /sys config\n",
                            "checkStatusnoret\n",
                            "tmsh create ltm pool ${APPNAME}-pool members add { ${POOLMEM}:${POOLMEMPORT} } monitor gateway_icmp\n",
                            "tmsh create ltm virtual /Common/${APPNAME}-${VIRTUALSERVERPORT} { destination 0.0.0.0:${VIRTUALSERVERPORT} ip-protocol tcp mask 255.255.255.255 pool /Common/${APPNAME}-pool source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n",
                            "tmsh save /sys config\n"
                            ]
                        ),
                        mode='000777',
                        owner='root',
                        group='root'
                    )
                } 
            ),
            commands={
                       "b-configure-BigIP" : {
                            "command" : "/tmp/firstrun.sh\n"
                        }
            }
        ) 
    })
)

BigIPInstance = t.add_resource(Instance(
    "BigIPInstance",
    Metadata=single_nic_metadata,
    UserData=Base64(Join("", ["#!/bin/bash\n", "/opt/aws/apitools/cfn-init-1.4-0.amzn1/bin/cfn-init -v -s ", Ref("AWS::StackId"), " -r BigIPInstance ", " --region ", Ref("AWS::Region"), "\n"])),
    Tags=Tags(
        Name=Join("", ["Big-IP: ", Ref("AWS::StackName")] ),
        Application=Ref("AWS::StackName"),
    ),
    ImageId=FindInMap("BigIPRegionMap", Ref("AWS::Region"), Ref(BigIPPerformanceType)),
    KeyName=Ref(KeyName),
    InstanceType=Ref(BigIPInstanceType),
    NetworkInterfaces=[
    NetworkInterfaceProperty(
        DeviceIndex="0",
        NetworkInterfaceId=Ref("ExternalInterface"),
        Description="Public or External Interface",
    ),
    ],
))


# Webserver = t.add_resource(Instance(
#     "Webserver",
#     UserData=Base64(Join("", ["#!/bin/bash -x\n", "echo \"Hello World\"\n"])),
#     Tags=Tags(
#         Name="Webserver",
#         Application=Ref("AWS::StackName"),
#     ),
#     ImageId=FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"), "AMI"),
#     KeyName=Ref(KeyName),
#     InstanceType=Ref(WebserverInstanceType),
#     NetworkInterfaces=[
#     NetworkInterfaceProperty(
#         SubnetId=Ref(AZ1ApplicationSubnet),
#         DeviceIndex="0",
#         GroupSet=[Ref("WebserverSecurityGroup")],
#         Description=Join("", [Ref("AWS::StackName"), " Webserver Network Interface"]),
#         AssociatePublicIpAddress="true",
#     ),
#     ],
# ))

### BEGIN OUTPUT

VpcID = t.add_output(Output(
    "VpcID",
    Description="VPC ID",
    Value=Ref(VPC),
))

AvailabilityZone = t.add_output(Output(
    "AvailabilityZone",
    Description="Availability Zone",
    Value=GetAtt(BigIPInstance, "AvailabilityZone"),
))

# AZ1ManagementSubnetID = t.add_output(Output(
#     "AZ1ManagementSubnetID",
#     Description="AZ1 Management Subnet ID",
#     Value=Ref(AZ1ManagementSubnet),
# ))

# Note: AZ1 part of name needs to be stripped
ExternalSubnetId = t.add_output(Output(
    "Az1ExternalSubnetId",
    Description="Az1 Public or External Subnet ID",
    Value=Ref(ExternalSubnetId),
))

# AZ1InternalSubnetID = t.add_output(Output(
#     "AZ1InternalSubnetID",
#     Description="AZ1 Private or Internal Subnet ID",
#     Value=Ref(AZ1InternalSubnet),
# ))

# AZ1ApplicationSubnetID = t.add_output(Output(
#     "AZ1ApplicationSubnetID",
#     Description="AZ1 Application Subnet ID",
#     Value=Ref(AZ1ApplicationSubnet),
# ))

BigIPInstanceID = t.add_output(Output(
    "BigIPInstanceId",
    Description="Instance ID of Big-IP in Amazon",
    Value=Ref(BigIPInstance),
))

BigIPExternalSecurityGroupId = t.add_output(Output(
    "BigIPExternalSecurityGroupId",
    Description="Public or External Security Group",
    Value=Ref(BigIPExternalSecurityGroupId),
))

ExternalInterfaceId = t.add_output(Output(
    "ExternalInterfaceId",
    Description="External interface ID on BIG-IP",
    Value=Ref(ExternalInterface),
))

ExternalInterfacePrivateIp = t.add_output(Output(
    "ExternalInterfacePrivateIp",
    Description="Internally routable IP of public interface on BIG-IP",
    Value=GetAtt(ExternalInterface, "PrimaryPrivateIpAddress"),
))

VipEipAddress = t.add_output(Output(
    "VipEipAddress",
    Description="EIP address for VIP",
    Value=Join("", ["http://", Ref(ExternalSelfEipAddress), ":80"]),
))

BigIPUrl = t.add_output(Output(
    "BigIPUrl",
    Description="BigIP Management GUI",
    Value=Join("", ["https://", GetAtt(BigIPInstance, "PublicIp"), ":", Ref(BigIPManagementGuiPort)]),
))

# WebserverPrivateIP = t.add_output(Output(
#     "WebserverPrivateIP",
#     Description="Private IP for Webserver",
#     Value=GetAtt(Webserver, "PrivateIp"),
# ))

# WebserverPublicIP = t.add_output(Output(
#     "WebserverPublicIP",
#     Description="Public IP for Webserver",
#     Value=GetAtt(Webserver, "PublicIp"),
# ))

# WebserverPublicURL = t.add_output(Output(
#     "WebserverPublicURL",
#     Description="Public URL for Webserver",
#     Value=Join("", ["http://", GetAtt(Webserver, "PublicIp")]),
# ))


print(t.to_json())

